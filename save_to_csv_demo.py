#!/usr/bin/env python3
"""
Demo script to show how to save data as CSV
This script demonstrates different ways to export data to CSV format
"""

import pandas as pd
import json
import csv
from pathlib import Path

def demo_csv_export():
    """Demonstrate various CSV export methods"""
    
    print("🔄 CSV Export Demo")
    print("=" * 50)
    
    # Method 1: Using pandas (most common and flexible)
    print("\n1️⃣ Method 1: Using pandas DataFrame")
    
    # Sample data
    sample_data = [
        {"name": "John Doe", "age": 30, "city": "New York", "salary": 75000},
        {"name": "Jane Smith", "age": 25, "city": "Los Angeles", "salary": 68000},
        {"name": "Bob Johnson", "age": 35, "city": "Chicago", "salary": 82000},
        {"name": "Alice Brown", "age": 28, "city": "Houston", "salary": 71000}
    ]
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(sample_data)
    df.to_csv("sample_data.csv", index=False)
    print("✅ Saved sample_data.csv using pandas")
    
    # Method 2: Using Python's built-in csv module
    print("\n2️⃣ Method 2: Using Python's built-in csv module")
    
    with open("sample_data_builtin.csv", "w", newline="", encoding="utf-8") as f:
        if sample_data:
            writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_data)
    print("✅ Saved sample_data_builtin.csv using built-in csv module")
    
    # Method 3: Export from JSON data (like your whitematter data)
    print("\n3️⃣ Method 3: Export from JSON data")
    
    try:
        # Load your whitematter data
        with open("Data/whitematter_data.json", "r") as f:
            whitematter_data = json.load(f)
        
        # Convert to DataFrame and save
        if whitematter_data:
            df_json = pd.DataFrame(whitematter_data)
            df_json.to_csv("whitematter_data_export.csv", index=False)
            print(f"✅ Exported {len(whitematter_data)} records to whitematter_data_export.csv")
            
            # Show first few rows
            print(f"\n📊 Preview of exported data:")
            print(df_json.head())
            
    except FileNotFoundError:
        print("❌ whitematter_data.json not found")
    except Exception as e:
        print(f"❌ Error loading JSON data: {e}")
    
    # Method 4: Custom CSV export with specific columns
    print("\n4️⃣ Method 4: Custom CSV export with selected columns")
    
    custom_data = [
        {"pmcid": "PMC123456", "title": "Study on White Matter", "modality": "DTI", "subjects": 50},
        {"pmcid": "PMC789012", "title": "Brain Imaging Research", "modality": "fMRI", "subjects": 30},
        {"pmcid": "PMC345678", "title": "Neuroimaging Analysis", "modality": "T1-MRI", "subjects": 75}
    ]
    
    # Export only specific columns
    df_custom = pd.DataFrame(custom_data)
    df_custom[["pmcid", "title", "modality"]].to_csv("custom_export.csv", index=False)
    print("✅ Saved custom_export.csv with selected columns only")
    
    print("\n🎉 CSV Export Demo Complete!")
    print("\nFiles created:")
    print("  - sample_data.csv")
    print("  - sample_data_builtin.csv") 
    print("  - whitematter_data_export.csv")
    print("  - custom_export.csv")

def show_csv_files():
    """Show the created CSV files"""
    print("\n📁 Created CSV files:")
    csv_files = list(Path(".").glob("*.csv"))
    for csv_file in csv_files:
        size = csv_file.stat().st_size
        print(f"  - {csv_file.name} ({size} bytes)")

if __name__ == "__main__":
    demo_csv_export()
    show_csv_files()
