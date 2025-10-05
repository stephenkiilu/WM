# Brain Imaging Paper Information Extraction

An automated information extraction system for brain imaging research papers using OpenAI's GPT-4o-mini API. This tool extracts structured data including imaging modalities, patient groups, white matter tracts, and subject information from neuroscience literature.

## Features

- **Automated Information Extraction**: Extract key information from brain imaging papers using GPT-4o-mini
- **Multiple Processing Modes**: 
  - Mode 1: No chunking (process entire paper at once)
  - Mode 2: Chunking (split body into sections for better accuracy)
  - Mode 3: Title, Abstract, Keywords only (fast processing)
- **Structured Output**: Results saved to CSV format for easy analysis
- **Batch Processing**: Process multiple papers with rate limiting to avoid API limits

## Extracted Information

The system extracts four key categories from each paper:

1. **Imaging Modalities**: Brain imaging techniques (e.g., fMRI, DTI, MRI)
2. **Patient Groups**: Clinical populations studied (e.g., Alzheimer's disease, Healthy controls)
3. **White Matter Tracts**: Specific white matter tract names (e.g., corpus callosum, arcuate fasciculus)
4. **Subjects**: Species studied (e.g., humans, mice, rats)

## Prerequisites

- Python 3.8+
- OpenAI API key (for GPT-4o-mini access)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "UT /2025/Meta LLM"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

Or configure it in `config.py`:
```python
OPENAI_API_KEY = "your_api_key_here"
```

## Project Structure

```
.
├── main.py                          # Main extraction pipeline
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── prompts/
│   └── brain_extraction.py         # System prompt for LLM extraction
├── data/
│   └── processed/
│       └── whitematter_data.json   # Input paper data
├── extracted_info.csv              # Output extraction results
└── README.md                       # This file
```

## Usage

### Basic Usage

```python
from main import extract_all
import json

# Load your paper data
with open("data/processed/whitematter_data.json", "r") as f:
    papers = json.load(f)

# Extract information from papers
results = extract_all(
    papers[0:10],                    # Process first 10 papers
    out_csv="extracted_info.csv",    # Output file
    model="gpt-4o-mini",             # OpenAI model
    sleep_sec=0.8,                   # Rate limiting delay
    processing_mode=1                # Processing mode
)
```

### Processing Modes

**Mode 1: No Chunking (Recommended for shorter papers)**
```python
extract_all(papers, processing_mode=1)
```
Combines title, abstract, keywords, and body into a single prompt.

**Mode 2: Chunking (Recommended for longer papers)**
```python
extract_all(papers, processing_mode=2)
```
Splits paper body into sections and processes each separately, then aggregates results.

**Mode 3: Title/Abstract/Keywords Only (Fast)**
```python
extract_all(papers, processing_mode=3)
```
Only processes metadata, skips full text (faster but may miss details).

### Single Paper Extraction

```python
from main import extract_one

paper = papers[0]
data = extract_one(paper, model="gpt-4o-mini", processing_mode=1)
print(data)
# Output: {
#   "imaging_modalities": ["fMRI", "DTI"],
#   "patient_groups": ["Alzheimer's disease", "Healthy controls"],
#   "whitematter_tracts": ["corpus callosum"],
#   "subjects": ["humans"]
# }
```

## Input Data Format

Papers should be provided as a list of dictionaries with the following structure:

```json
{
  "pmcid": "PMC1234567",
  "title": "Paper title",
  "abstract": "Paper abstract...",
  "keywords": "keyword1, keyword2",
  "body": "## Introduction\n\nPaper content..."
}
```

## Output Format

Results are saved as a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `pmcid` | PubMed Central ID |
| `title` | Paper title |
| `imaging_modalities` | Semicolon-separated list of imaging techniques |
| `patient_groups` | Semicolon-separated list of patient populations |
| `whitematter_tracts` | Semicolon-separated list of white matter tracts |
| `subjects` | Semicolon-separated list of subjects studied |

## API Costs

This project uses OpenAI's **GPT-4o-mini** API:
- Cost-effective for large-scale extraction
- Rate limiting implemented (`sleep_sec` parameter) to avoid hitting API limits
- Typical cost: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens

## Configuration

### Adjusting Rate Limits

Modify the `sleep_sec` parameter to control API call frequency:
```python
extract_all(papers, sleep_sec=1.0)  # Wait 1 second between calls
```

### Changing the Model

You can use different OpenAI models:
```python
extract_all(papers, model="gpt-4o")  # More expensive but potentially more accurate
```

## Customizing Extraction

To modify what information is extracted, edit the system prompt in `prompts/brain_extraction.py`:

```python
SYSTEM_PROMPT = """You are an information extraction expert...
- Add your custom fields here
"""
```

## Troubleshooting

**API Key Issues**
- Ensure `.env` file is in the project root
- Verify API key is valid and has sufficient credits

**Rate Limiting Errors**
- Increase `sleep_sec` parameter
- Check your OpenAI account rate limits

**Memory Issues with Large Papers**
- Use processing_mode=2 (chunking) for very long papers
- Use processing_mode=3 to skip body text

## Dependencies

Key dependencies include:
- `openai` - OpenAI API client
- `pandas` - Data manipulation and CSV output
- `python-dotenv` - Environment variable management
- `neuroquery` - Neuroscience text analysis
- `nilearn` - Neuroimaging data processing

See `requirements.txt` for complete list.

## License

[Add your license here]

## Citation

If you use this tool in your research, please cite:
[Add citation information]

## Contact

For questions or issues, please contact [your contact information]
