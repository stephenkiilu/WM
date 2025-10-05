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


def extract_one(WM_paper: Dict[str, Any], model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """Extract information from a single paper using the OpenAI API.
    Args:
        WM_paper (Dict[str, Any]): A dictionary containing paper details.
        model (str): The model to use for extraction.
    Returns:
        Dict[str, Any]: Extracted data from the paper.
    """
    user_payload = {
        "title": WM_paper.get("title", ""),
        "abstract": WM_paper.get("abstract", ""),
        "keywords": WM_paper.get("keywords", "")
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
    except Exception:
        data = {
            "imaging_modalities": [],
            "patient_groups": [],
            "whitematter_tracts": [],
            "subjects": []
        }
    return data


def extract_all(WM_papers: List[Dict[str, Any]],
                out_csv: str = "extracted_info.csv",
                model: str = "gpt-4o-mini",
                sleep_sec: float = 0.8) -> List[Dict[str, Any]]:
    """"Extract information from multiple papers and save to a CSV file.
    Args:
        WM_papers (List[Dict[str, Any]]): List of dictionaries containing paper details.
        out_csv (str): Output CSV file path.
        model (str): The model to use for extraction.
        sleep_sec (float): Sleep time between API calls to avoid rate limits.
    Returns:
        List[Dict[str, Any]]: List of extracted data from all papers.
    """
    results = []
    for i, paper in enumerate(WM_papers, 1):
        data = extract_one(paper, model=model)
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

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["pmcid","title","imaging_modalities","patient_groups","whitematter_tracts","subjects"]
        )
        writer.writeheader()
        writer.writerows(results)

    return results


extract_one(whitematter_json[10])
# extract_all(whitematter_json[0:10], out_csv="test.csv")

#csv to excel
data_csv = pd.read_csv('test.csv')
# data_csv.to_excel('test.xlsx', index=False)

whitematter_json[10]

data=pd.read_csv('test.csv')


# %%
