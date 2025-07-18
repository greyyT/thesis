import json
import os
import csv
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load JSONL file and return list of resume objects"""
    resumes = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    resumes.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                    continue
    return resumes

def extract_resume_data(resume_obj: Dict[str, Any]) -> Dict[str, Any]:
    """Extract content and annotations from resume object"""
    content = resume_obj.get('content', '')
    annotations = resume_obj.get('annotation', [])
    
    # Extract key information from annotations
    skills = []
    designations = []
    companies = []
    education = []
    
    for annotation in annotations:
        label = annotation.get('label', [])
        points = annotation.get('points', [])
        
        for point in points:
            text = point.get('text', '').strip()
            if 'Skills' in label:
                skills.append(text)
            elif 'Designation' in label:
                designations.append(text)
            elif 'Companies worked at' in label:
                companies.append(text)
            elif 'Degree' in label or 'College Name' in label:
                education.append(text)
    
    return {
        'content': content,
        'skills': skills,
        'designations': designations,
        'companies': companies,
        'education': education
    }

def predict_job_position(client: OpenAI, resume_data: Dict[str, Any]) -> str:
    """Use Gemini model to predict top 1 relevant job position"""
    
    # Create prompt with resume information
    prompt = f"""
Based on the following resume information, predict the top 1 most relevant job position for this candidate:

Resume Content:
{resume_data['content'][:1000]}...

Key Skills: {', '.join(resume_data['skills'][:5])}
Previous Designations: {', '.join(resume_data['designations'][:3])}
Companies: {', '.join(resume_data['companies'][:3])}
Education: {', '.join(resume_data['education'][:3])}

Please provide only the job position title (e.g., "Software Engineer", "Data Scientist", "Product Manager").
"""
    
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash-preview-05-20",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error predicting job position: {e}")
        return "Unknown"

def main():
    # Load environment variables
    load_dotenv()
    
    # Set up OpenRouter client
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("Please set OPENROUTER_API_KEY environment variable")
        return
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Load resume data
    jsonl_file = "../data/Entity Recognition in Resumes.jsonl"
    resumes = load_jsonl(jsonl_file)
    
    print(f"Loaded {len(resumes)} resumes")
    
    # Results storage
    results = []
    
    # Process each resume
    for i, resume in enumerate(resumes):  # Process all resumes
        print(f"\n--- Resume {i+1} ---")
        
        try:
            # Extract resume data
            resume_data = extract_resume_data(resume)
            
            # Get job position prediction
            predicted_position = predict_job_position(client, resume_data)
            
            print(f"Predicted Job Position: {predicted_position}")
            
            # Print some extracted info for verification
            if resume_data['designations']:
                print(f"Previous Designations: {resume_data['designations'][:2]}")
            if resume_data['skills']:
                print(f"Key Skills: {resume_data['skills'][:3]}")
            
            # Store results
            results.append({
                'resume_id': i + 1,
                'predicted_position': predicted_position,
                'previous_designations': ', '.join(resume_data['designations'][:3]),
                'key_skills': ', '.join(resume_data['skills'][:5]),
                'companies': ', '.join(resume_data['companies'][:3]),
                'education': ', '.join(resume_data['education'][:3])
            })
            
        except Exception as e:
            print(f"Error processing resume {i+1}: {e}")
            continue
    
    # Export results to CSV
    output_file = "../data/resume_job_predictions.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['resume_id', 'predicted_position', 'previous_designations', 'key_skills', 'companies', 'education']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults exported to {output_file}")
    print(f"Total processed: {len(results)} resumes")

if __name__ == "__main__":
    main()