#!/usr/bin/env python3
"""
Unify resume prediction datasets from different sources.
Combines resume_job_predictions.csv and updated_dataset_predictions_async.csv
into a single unified dataset with standardized schema.
"""

import pandas as pd
import numpy as np
import os


def load_and_analyze_datasets():
    """Load both datasets and print their schemas."""
    print("Loading datasets...")
    
    # Load first dataset (from Entity Recognition in Resumes.jsonl)
    df1 = pd.read_csv('../data/resume_job_predictions.csv')
    print(f"\nDataset 1 (resume_job_predictions.csv):")
    print(f"  - Shape: {df1.shape}")
    print(f"  - Columns: {list(df1.columns)}")
    
    # Load second dataset (from UpdatedResumeDataSet.csv)
    df2 = pd.read_csv('../data/updated_dataset_predictions_async.csv')
    print(f"\nDataset 2 (updated_dataset_predictions_async.csv):")
    print(f"  - Shape: {df2.shape}")
    print(f"  - Columns: {list(df2.columns)}")
    
    return df1, df2


def standardize_datasets(df1, df2):
    """Standardize column names and add missing fields."""
    print("\nStandardizing datasets...")
    
    # Add source tracking
    df1['source_dataset'] = 'entity_recognition'
    df2['source_dataset'] = 'updated_resume'
    
    # Standardize df1 (add missing fields and rename columns)
    df1['actual_category'] = np.nan  # No ground truth in this dataset
    df1['skills'] = df1['key_skills']
    df1['experience'] = df1['previous_designations']
    
    # Standardize df2 (add missing companies field)
    df2['companies'] = np.nan
    
    # Select and reorder columns for unified schema
    columns = ['resume_id', 'source_dataset', 'actual_category', 
               'predicted_position', 'skills', 'education', 
               'experience', 'companies']
    
    df1_unified = df1[columns].copy()
    df2_unified = df2[columns].copy()
    
    return df1_unified, df2_unified


def create_unified_dataset(df1_unified, df2_unified):
    """Combine standardized datasets into a single unified dataset."""
    print("\nCreating unified dataset...")
    
    # Combine datasets
    unified_df = pd.concat([df1_unified, df2_unified], ignore_index=True)
    
    # Add unique ID across both datasets
    unified_df['unified_id'] = range(1, len(unified_df) + 1)
    
    # Reorder columns with unified_id first
    column_order = ['unified_id'] + [col for col in unified_df.columns if col != 'unified_id']
    unified_df = unified_df[column_order]
    
    return unified_df


def analyze_unified_dataset(unified_df, df2):
    """Print analysis and statistics of the unified dataset."""
    print("\n" + "="*60)
    print("UNIFIED DATASET ANALYSIS")
    print("="*60)
    
    # Basic statistics
    print(f"\nTotal records: {len(unified_df)}")
    print(f"Records from entity_recognition: {(unified_df['source_dataset'] == 'entity_recognition').sum()}")
    print(f"Records from updated_resume: {(unified_df['source_dataset'] == 'updated_resume').sum()}")
    
    # Predicted position distribution
    print("\nTop 10 Predicted Positions:")
    print(unified_df['predicted_position'].value_counts().head(10))
    
    # Accuracy metrics (only for dataset 2 which has actual categories)
    df2_in_unified = unified_df[unified_df['source_dataset'] == 'updated_resume'].copy()
    if len(df2_in_unified) > 0:
        accuracy_mask = df2_in_unified['actual_category'].str.lower() == df2_in_unified['predicted_position'].str.lower()
        accuracy = accuracy_mask.mean()
        print(f"\nAccuracy Metrics (Dataset 2 only):")
        print(f"  - Overall accuracy: {accuracy:.2%}")
        print(f"  - Correct predictions: {accuracy_mask.sum()}")
        print(f"  - Total predictions: {len(df2_in_unified)}")
        
        # Accuracy by category
        print("\nAccuracy by Category (top 10):")
        category_accuracy = df2_in_unified.groupby('actual_category').apply(
            lambda x: (x['actual_category'].str.lower() == x['predicted_position'].str.lower()).mean()
        ).sort_values(ascending=False).head(10)
        for category, acc in category_accuracy.items():
            count = (df2_in_unified['actual_category'] == category).sum()
            print(f"  - {category}: {acc:.2%} ({count} samples)")
    
    # Data completeness
    print("\nData Completeness:")
    for col in unified_df.columns:
        missing = unified_df[col].isna().sum()
        missing_pct = (missing / len(unified_df)) * 100
        print(f"  - {col}: {len(unified_df) - missing}/{len(unified_df)} ({100-missing_pct:.1f}% complete)")


def main():
    """Main execution function."""
    # Check if input files exist
    if not os.path.exists('../data/resume_job_predictions.csv'):
        print("Error: resume_job_predictions.csv not found!")
        return
    
    if not os.path.exists('../data/updated_dataset_predictions_async.csv'):
        print("Error: updated_dataset_predictions_async.csv not found!")
        return
    
    # Load datasets
    df1, df2 = load_and_analyze_datasets()
    
    # Standardize datasets
    df1_unified, df2_unified = standardize_datasets(df1, df2)
    
    # Create unified dataset
    unified_df = create_unified_dataset(df1_unified, df2_unified)
    
    # Save unified dataset
    output_file = '../data/unified_resume_predictions.csv'
    unified_df.to_csv(output_file, index=False)
    print(f"\nUnified dataset saved to: {output_file}")
    
    # Analyze and print statistics
    analyze_unified_dataset(unified_df, df2)
    
    # Print sample records
    print("\n" + "="*60)
    print("SAMPLE RECORDS FROM UNIFIED DATASET")
    print("="*60)
    print("\nFirst 3 records from entity_recognition source:")
    print(unified_df[unified_df['source_dataset'] == 'entity_recognition'].head(3).to_string())
    
    print("\nFirst 3 records from updated_resume source:")
    print(unified_df[unified_df['source_dataset'] == 'updated_resume'].head(3).to_string())


if __name__ == "__main__":
    main()