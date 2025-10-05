# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import scipy as sp
import json, pprint, itertools
from neuroquery import fetch_neuroquery_model, NeuroQueryModel
from nilearn.plotting import view_img
import glob
from pathlib import Path
import os, json, csv, time
from openai import OpenAI
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

#import for openai
from config import OPENAI_API_KEY
from prompts.brain_extraction import SYSTEM_PROMPT
client = OpenAI(api_key=OPENAI_API_KEY)

WHITEMATTER_JSON_PATH = "data/processed/whitematter_data.json"
with open(WHITEMATTER_JSON_PATH, "r", encoding="utf-8") as f:
    whitematter_json = json.load(f)

#data fields
imaging_modalities =["Anatomical MRI","fMRI","DTI","PET","CT","SPECT","MEG","EEG"]
patient_groups=["Alzheimer's disease","Bipolar","Healthy controls"]
whitematter_tracts =["Corpus Callosum","Cingulum","Uncinate Fasciculus","Superior Longitudinal Fasciculus","Inferior Longitudinal Fasciculus","Fornix","Arcuate Fasciculus","Corticospinal Tract"]
subjects=["humans","mice","rats","monkeys"]

def process_full_data(paper: Dict[str, Any]) -> str:
    """
    Preprocess full data including title, abstract, keywords, and chunked body by sections.
    Combine subsections with their main section (e.g., intro + background, results + findings).
    """
    body = paper.get("body", "")
    abstract = paper.get("abstract", "")
    title = paper.get("title", "")
    keywords = paper.get("keywords", "")
    
    # Combine title, abstract, and keywords into one section (first chunk)
    full_data = title + " " + abstract + " " + keywords

    # Split the body by '##' to capture major sections (e.g., intro, results)
    sections = body.split("##")
    body_chunks = []
    current_section = ""

    for section in sections:
        # Clean the section
        section = section.strip()
        if not section:
            continue
        
        # If the section starts with '#' (subsection), combine it with the previous section
        if section.startswith("#"):
            current_section += " " + section
        else:
            # If there's a current section, add it to body_chunks
            if current_section:
                body_chunks.append(current_section.strip())
            # Start a new section (i.e., for the '##' section)
            current_section = section.strip()

    # Append the last section if it exists
    if current_section:
        body_chunks.append(current_section.strip())

    return full_data, body_chunks



abstract, body_chunks  = process_full_data(whitematter_json[0])


def extract_one(WM_paper: Dict[str, Any], model: str = "gpt-4o-mini", use_full_data: bool = False) -> Dict[str, Any]:
    """
    Extract data from a single paper, with the option to use all data (including chunked body).
    Args:
        WM_paper (Dict[str, Any]): A dictionary containing paper details.
        model (str): The model to use for extraction.
        use_full_data (bool): Whether to use full data including chunked body.
    Returns:
        Dict[str, Any]: Extracted data from the paper.
    Use full data: True to include body chunking (title,abstract,main body sections e.g intro, methods, results, conclusions), False to use only title, abstract, and keywords.
    """
    if use_full_data:
        full_data, body_chunks = process_full_data(WM_paper)
        chunks = [full_data] + body_chunks  # Treat the full data as one chunk followed by body chunks
    else:
        # Use only the title, abstract, and keywords without chunking
        full_data = WM_paper.get("title", "") + " " + WM_paper.get("abstract", "") + " " + WM_paper.get("keywords", "")
        chunks = [full_data]  # No body chunks

    all_data = {
        "imaging_modalities": [],
        "patient_groups": [],
        "whitematter_tracts": [],
        "subjects": []
    }

    for chunk in chunks:
        user_payload = {
            "body": chunk  # Only include the chunk as the body
        }
        
        resp = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
            ]
        )
        
        content = resp.choices[0].message.content
        try:
            data = json.loads(content)
            # Aggregate the data from all chunks
            for key in all_data:
                all_data[key].extend(data.get(key, []))
        except Exception:
            pass

    # Remove duplicates and return the final data
    for key in all_data:
        all_data[key] = list(set(all_data[key]))

    return all_data


def extract_all(WM_papers: List[Dict[str, Any]],
                out_csv: str = "extracted_info.csv",
                model: str = "gpt-4o-mini",
                sleep_sec: float = 0.8,
                use_full_data: bool = False) -> List[Dict[str, Any]]:
    """
    Extract data from all papers and save to CSV, with option to use full data (body chunking).
    Args:
        WM_papers (List[Dict[str, Any]]): List of dictionaries containing paper details.
        out_csv (str): Output CSV file path.
        model (str): The model to use for extraction.
        sleep_sec (float): Sleep time between API calls to avoid rate limits.       
        use_full_data (bool): Whether to use full data including chunked body.
    Returns:
        List[Dict[str, Any]]: List of extracted data from all papers.
    """
    results = []
    for i, paper in enumerate(WM_papers, 1):
        data = extract_one(paper, model=model, use_full_data=use_full_data)
        row = {
            "pmcid": paper.get("pmcid", ""),
            "title": paper.get("title", ""),
            "imaging_modalities": ";".join(data.get("imaging_modalities", [])),
            "patient_groups": ";".join(data.get("patient_groups", [])),
            "whitematter_tracts": ";".join(data.get("whitematter_tracts", [])),
            "subjects": ";".join(data.get("subjects", []))
        }
        results.append(row)
        print(f"Processed {i}/{len(WM_papers)}")
        time.sleep(sleep_sec)

    # Write results to CSV
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["pmcid", "title", "imaging_modalities", "patient_groups", "whitematter_tracts", "subjects"]
        )
        writer.writeheader()
        writer.writerows(results)

    return results


#read json file

one_paper=extract_one(whitematter_json[0], use_full_data=True)




