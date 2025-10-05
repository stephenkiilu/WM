# %%
import os
import pandas as pd
import json
from dotenv import load_dotenv

# Load environment variables (e.g., API keys, etc.)
load_dotenv()  # Load environment variables from .env file

# Paths for data
RAW_DATA_PATH = 'data/raw'  # Raw data 
PROCESSED_DATA_PATH = 'data/processed'  # Processed data directory

# Create processed directory if it doesn't exist
#os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)  # Ensure the directory exists

os.path.dirname(os.path.dirname(__file__))

def get_file_path(file_name: str, folder: str = 'raw') -> str:
    """Generate and return the absolute file path for the data."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', folder, file_name)

def load_raw_data(file_name: str) -> pd.DataFrame:
    """Load raw data from the specified file."""
    file_path = get_file_path(file_name, 'raw')
    return pd.read_csv(file_path)

def save_processed_data(df: pd.DataFrame, file_name: str):
    """Save processed data to the specified processed data directory."""
    file_path = get_file_path(file_name, 'processed')
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

def process_data():
    """Main data processing function."""
    # Load raw data
    WM_data = load_raw_data('WM_data.csv')  # Read raw data
      
    # Extract PMCID column
    pmcids = WM_data['PMCID']  

    # Strip 'PMC' from the PMCID column
    pmcids = pmcids.str.replace('PMC', '', regex=False)  # Remove 'PMC' prefix

    # Save cleaned pmcids to processed folder
    pmcids.to_csv(get_file_path('pmcid.txt', 'processed'), index=False, header=False)  # Save to processed folder

    # Read pmcid.txt, clean the PMC IDs and save them
    pmcid_ids = pd.read_csv(get_file_path('pmcid.txt', 'processed'), header=None, names=["pmcid"])
    save_processed_data(pmcid_ids, 'pmcids.csv')

    # Read extracted data
    text_csv = pd.read_csv(get_file_path('text.csv', 'raw'))
    ordered_ids = pd.read_csv(get_file_path('pmcids.csv', 'processed'))

    # Merge the data on PMCID
    ordered_text = ordered_ids.merge(
        text_csv[["pmcid", "title", "keywords", "abstract", "body"]],
        on="pmcid",
        how="left",
        validate="1:1"
    )

    # Save ordered text data to processed folder
    save_processed_data(ordered_text, 'ordered_txt.csv')

    # Generate JSON from processed data
    generate_json_file(ordered_text)

def generate_json_file(data, output="whitematter_data.json"):
    """Generate a JSON file from the processed data."""
    whitematter_pmcid = data['pmcid'].tolist()
    whitematter_title = data['title'].tolist()
    whitematter_keyword = data['keywords'].tolist()  # Not used but extracted
    whitematter_abstract = data['abstract'].tolist()
    whitematter_body = data['body'].tolist()

    # Prepare the data for JSON
    whitematter_json = []
    for pmcid, abstract, title, keyword, body in zip(whitematter_pmcid, whitematter_abstract, whitematter_title, whitematter_keyword, whitematter_body):
        whitematter_json.append({
            "pmcid": pmcid,
            "title": title,
            "keywords": keyword,
            "abstract": abstract,
            "body": body
        })

    # Save JSON to output file
    output_path = get_file_path(output, "processed")  # Save to processed folder
    with open(output_path, "w") as f:
        json.dump(whitematter_json, f, indent=4, ensure_ascii=False)

    print(f"JSON data saved to {output_path}")

def save_abstract_data(json_file="whitematter_data.json"):
    """Extract abstracts and save to JSON."""
    # Read JSON file
    json_file = get_file_path(json_file, 'processed')
    with open(json_file, "r", encoding="utf-8") as f:
        whitematter_json = json.load(f)

    # Extract abstract data
    abstract_data = [{k: v for k, v in d.items() if k != "body" and k != "pmcid"} for d in whitematter_json]

    # Save abstract data to JSON file
    abstract_output_path = get_file_path('whitematter_abstract.json', 'processed')  # Save to processed folder
    with open(abstract_output_path, "w", encoding="utf-8") as f:
        json.dump(abstract_data, f, indent=4, ensure_ascii=False)

    print(f"Abstract JSON data saved to {abstract_output_path}")

# Run the data processing functions
process_data()
ordered_csv = load_raw_data(get_file_path('ordered_txt.csv', 'processed'))
generate_json_file(ordered_csv)
save_abstract_data()


