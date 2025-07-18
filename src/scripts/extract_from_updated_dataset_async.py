#!/usr/bin/env python3
"""
Extract and predict job positions from UpdatedResumeDataSet.csv using OpenRouter API with asyncio.
This script processes resumes concurrently while respecting rate limits.
"""

import pandas as pd
import os
import json
from openai import AsyncOpenAI
import asyncio
import time
from typing import Dict, Optional, List, Tuple
from dotenv import load_dotenv


async def extract_and_predict_async(
    client: AsyncOpenAI, 
    resume_text: str, 
    actual_category: str,
    semaphore: asyncio.Semaphore,
    retry_count: int = 3
) -> Optional[Dict[str, str]]:
    """Use LLM to extract features and predict job position in one call."""
    
    async with semaphore:  # Limit concurrent requests
        # Build prompt
        prompt = f"""Extract information from this resume and predict job position.

Resume Text:
{resume_text}

Return ONLY a JSON object with these fields:
{{
"skills": "key technical and soft skills",
"education": "educational background",
"experience": "work experience summary",
"predicted_position": "one of: Java Developer, Testing, DevOps Engineer, Python Developer, Web Designing, HR, Hadoop, Blockchain, ETL Developer, Operations Manager, Data Science, Sales, Mechanical Engineer, Arts, Database, Electrical Engineering, Health and fitness, PMO, Business Analyst, DotNet Developer, Automation Testing, Network Security Engineer, SAP Developer, Civil Engineer, Advocate"
}}

Do not include any text before or after the JSON."""

        for attempt in range(retry_count):
            try:
                response = await client.chat.completions.create(
                    model="google/gemini-2.5-flash",
                    messages=[
                        {"role": "system", "content": "You are a JSON API that extracts resume information. Output only valid JSON, no explanations or additional text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                )
                
                result_text = response.choices[0].message.content.strip()
                
                # Try to parse JSON response
                try:
                    # Remove markdown code blocks if present
                    if "```json" in result_text:
                        result_text = result_text.replace("```json", "").replace("```", "").strip()
                    elif "```" in result_text:
                        result_text = result_text.replace("```", "").strip()
                    
                    # Remove any thinking markers if present
                    if "◁think▷" in result_text or "◁/think▷" in result_text:
                        # Extract JSON from the response - find the last occurrence of JSON
                        # Split by end thinking marker and take the part after it
                        if "◁/think▷" in result_text:
                            parts = result_text.split("◁/think▷")
                            if len(parts) > 1:
                                result_text = parts[-1].strip()
                        
                        # Now extract JSON
                        json_start = result_text.find("{")
                        json_end = result_text.rfind("}") + 1
                        if json_start != -1 and json_end > json_start:
                            result_text = result_text[json_start:json_end]
                    
                    result = json.loads(result_text)
                    return result
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON: {e}")
                    print(f"Raw response: {result_text[:200]}...")
                    return None
                    
            except Exception as e:
                if "rate" in str(e).lower() and attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 5  # Exponential backoff
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"API error: {e}")
                    return None
        
        return None


async def process_batch(
    client: AsyncOpenAI,
    batch_data: List[Tuple[int, pd.Series]],
    semaphore: asyncio.Semaphore
) -> List[Tuple[int, Optional[Dict], str]]:
    """Process a batch of resumes concurrently."""
    tasks = []
    
    for idx, row in batch_data:
        task = extract_and_predict_async(client, row['Resume'], row['Category'], semaphore)
        tasks.append((idx, task, row['Category']))
    
    # Run all tasks concurrently
    results = []
    for idx, task, category in tasks:
        result = await task
        results.append((idx, result, category))
    
    return results


async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        print("Please add OPENROUTER_API_KEY to your .env file or set it as an environment variable")
        return
    
    # Initialize Async OpenAI client with OpenRouter base URL
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    # Load dataset
    print("Loading UpdatedResumeDataSet.csv...")
    df = pd.read_csv("../data/UpdatedResumeDataSet.csv")
    print(f"Loaded {len(df)} resumes")
    
    # Configuration
    concurrent_limit = 5  # Number of concurrent requests
    batch_size = 20  # Resumes per batch (respecting rate limit)
    semaphore = asyncio.Semaphore(concurrent_limit)
    
    results = []
    failed_count = 0
    save_interval = 50  # Save every 50 resumes
    
    # Process in batches
    total_batches = (len(df) + batch_size - 1) // batch_size
    print(f"\nProcessing {len(df)} resumes in {total_batches} batches...")
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(df))
        batch_data = [(idx, row) for idx, row in df.iloc[start_idx:end_idx].iterrows()]
        
        print(f"\nBatch {batch_num + 1}/{total_batches}: Processing resumes {start_idx + 1}-{end_idx}...")
        batch_start_time = time.time()
        
        # Process batch concurrently
        batch_results = await process_batch(client, batch_data, semaphore)
        
        # Process results
        for idx, result, actual_category in batch_results:
            if result:
                final_result = {
                    'resume_id': idx,
                    'actual_category': actual_category,
                    'predicted_position': result.get('predicted_position', ''),
                    'skills': result.get('skills', ''),
                    'education': result.get('education', ''),
                    'experience': result.get('experience', '')
                }
                results.append(final_result)
                print(f"Resume {idx}: Success")
            else:
                failed_count += 1
                print(f"Resume {idx}: Failed")
        
        # Periodic saving
        if len(results) >= save_interval and len(results) % save_interval <= batch_size:
            print(f"\nSaving intermediate results ({len(results)} resumes processed)...")
            results_df = pd.DataFrame(results)
            output_file = "../data/updated_dataset_predictions_async.csv"
            results_df.to_csv(output_file, index=False)
            print(f"Intermediate save complete. Successful: {len(results)}, Failed: {failed_count}")
        
        # Rate limiting: Wait if batch processed too quickly
        batch_duration = time.time() - batch_start_time
        if batch_duration < 60 and batch_num < total_batches - 1:  # 60 seconds = 1 minute
            wait_time = 60 - batch_duration
            print(f"Waiting {wait_time:.1f}s to respect rate limit...")
            await asyncio.sleep(wait_time)
    
    # Save final results
    if results:
        results_df = pd.DataFrame(results)
        output_file = "../data/updated_dataset_predictions_async.csv"
        results_df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")
        print(f"Total processed: {len(results) + failed_count}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {failed_count}")
        
        # Calculate accuracy
        correct = sum(1 for r in results if r['actual_category'].lower() == r['predicted_position'].lower())
        accuracy = correct / len(results) * 100 if results else 0
        print(f"\nAccuracy: {accuracy:.2f}% ({correct}/{len(results)})")
        
        # Show category distribution
        print("\nPrediction distribution:")
        print(results_df['predicted_position'].value_counts().head(10))
    else:
        print("No results to save")


if __name__ == "__main__":
    asyncio.run(main())