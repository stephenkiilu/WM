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

def process_full_data(paper: Dict[str, Any], processing_mode: int) -> str:
    """
    Preprocess the data according to the selected processing mode:
    1. No chunking: Combine all data (title, abstract, keywords, and body).
    2. Chunking: Abstract + body (split body into chunks).
    3. Title, Abstract, Keywords: Only include title, abstract, and keywords, no body.
    """
    # Convert all fields to strings to handle NaN/float values
    body = str(paper.get("body", "")) if paper.get("body") is not None else ""
    abstract = str(paper.get("abstract", "")) if paper.get("abstract") is not None else ""
    title = str(paper.get("title", "")) if paper.get("title") is not None else ""
    keywords = str(paper.get("keywords", "")) if paper.get("keywords") is not None else ""

    if processing_mode == 1:
        # No chunking: Combine all data (title, abstract, keywords, and body)
        full_data = title + " " + abstract + " " + keywords + " " + body
        return full_data, []

    elif processing_mode == 2:
        # Chunking: Combine abstract + body in chunks (split body into sections)
        full_data = title + " " + abstract + " " + keywords
        sections = body.split("##")  # Split the body by sections marked with '##'
        body_chunks = []
        current_section = ""

        for section in sections:
            section = section.strip()
            if not section:
                continue
            if section.startswith("#"):  # If it's a subsection (starts with '###')
                current_section += " " + section
            else:
                if current_section:
                    body_chunks.append(current_section.strip())
                current_section = section.strip()

        if current_section:
            body_chunks.append(current_section.strip())

        return full_data, body_chunks

    elif processing_mode == 3:
        # Just Title, Abstract, Keywords: Only include title, abstract, and keywords
        full_data = title + " " + abstract + " " + keywords
        return full_data, []

    return "", []  # Default case if invalid processing_mode


def extract_one(WM_paper: Dict[str, Any], model: str = "gpt-4o-mini", processing_mode: int = 1) -> Dict[str, Any]:
    """
    Extract data from a single paper based on the selected processing mode.
    Args:
        WM_paper (Dict[str, Any]): A dictionary containing paper details.
        model (str): The model to use for extraction.
        processing_mode (int): 
        1. No chunking: Combine all data (title, abstract, keywords, and body).
        2. Chunking: Abstract + body (split body into chunks).
        3. Title, Abstract, Keywords: Only include title, abstract, and keywords, no body.
    Returns:
        Dict[str, Any]: Extracted data from the paper.
    """
    full_data, body_chunks = process_full_data(WM_paper, processing_mode)

    # If we are chunking, we have multiple chunks; otherwise, we have just one chunk
    if processing_mode == 1 or processing_mode == 3:
        chunks = [full_data]
    else:
        chunks = [full_data] + body_chunks  # Combine full data (title, abstract, keywords) + body chunks

    all_data = {"subjects": [],
        "patient_groups": [],
        "imaging_modalities": [],
        "whitematter_tracts": [],               
        "analysis_software": [],
        "study_type": [],
        "diffusion_measures": [],
        "template_space": [],
        "results_method": [],
        "white_integrity": [],
        "question_of_study": [],
    }

    for chunk in chunks:
        user_payload = {
            "body": chunk  # Send the chunk as the body content
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
                    if isinstance(data.get(key), list):
                        all_data[key].extend(data[key])
                    elif data.get(key):  # Handle case where API returns string instead of list
                        all_data[key].append(data[key])
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw content: {content}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            print(f"Raw content: {content}")

    # Remove duplicates and return the final data
    for key in all_data:
        if isinstance(all_data[key], list):
            all_data[key] = list(set(all_data[key]))

    return all_data


def extract_all(WM_papers: List[Dict[str, Any]],
                out_csv: str = "extracted_info.csv",
                model: str = "gpt-4o-mini",
                sleep_sec: float = 0.8,
                processing_mode: int = 1) -> List[Dict[str, Any]]:
    """
    Extract data from all papers and save to CSV, with option to select processing mode.
    Args:
        WM_papers (List[Dict[str, Any]]): List of dictionaries containing paper details.
        out_csv (str): Output CSV file path.
        model (str): The model to use for extraction.
        sleep_sec (float): Sleep time between API calls to avoid rate limits.       
        processing_mode (int): The mode of processing (1: No chunking, 2: Chunking, 3: Title, Abstract, Keywords only).
    Returns:
        List[Dict[str, Any]]: List of extracted data from all papers.   
    """
    results = []
    for i, paper in enumerate(WM_papers, 1):
        data = extract_one(paper, model=model, processing_mode=processing_mode)
        row = {
            "pmcid": paper.get("pmcid", ""),
            "title": paper.get("title", ""),
            "subjects": ";".join(data.get("subjects", [])),
            "patient_groups": ";".join(data.get("patient_groups", [])),
            "imaging_modalities": ";".join(data.get("imaging_modalities", [])),
            "whitematter_tracts": ";".join(data.get("whitematter_tracts", [])),
            "analysis_software": ";".join(data.get("analysis_software", [])),
            "study_type": ";".join(data.get("study_type", [])),
            "diffusion_measures": ";".join(data.get("diffusion_measures", [])),
            "template_space": ";".join(data.get("template_space", [])),
            "results_method": ";".join(data.get("results_method", [])),
            "white_integrity": ";".join(data.get("white_integrity", [])),
            "question_of_study": ";".join(data.get("question_of_study", [])),
        }
        results.append(row)
        print(f"Processed {i}/{len(WM_papers)}")
        time.sleep(sleep_sec)

    # Write results to CSV
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["pmcid", "title","subjects", "patient_groups", "imaging_modalities", "whitematter_tracts","analysis_software","study_type","diffusion_measures","template_space","results_method","white_integrity","question_of_study"]
        )
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ Successfully saved {len(results)} records to {out_csv}")

    return results

extract_all(whitematter_json[0:3], processing_mode=1)






