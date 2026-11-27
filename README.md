# 📚 Educational Search Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Information%20Retrieval-Search-0D9488?style=for-the-badge" alt="Information Retrieval">
</p>

<p align="center">
  <b>A focused educational search engine for discovering, indexing, and retrieving learning resources.</b>
</p>

---

## Project Overview

Edu-Search-Engine helps users search for educational resources using text and voice.

## 📖 About the Project

Educational Search Engine is an Information Retrieval project that collects educational web pages and PDFs, processes their content, and provides ranked search results through an interactive Streamlit interface.

Unlike a general-purpose search engine, it focuses on approved educational domains and builds a growing local corpus through automated crawling and scraping.

The system supports Boolean search, relevance ranking, text preprocessing, and evaluation.

## ✨ Features

- 🔍 Topic-based discovery of educational resources.
- 🌐 Focused crawling of approved educational websites.
- 📄 Automatic collection and extraction of web pages and PDFs.
- 🧠 English text normalization using NLTK and WordNet.
- 📚 Inverted index for efficient document retrieval.
- ⚡ Boolean search using AND, OR, and NOT.
- 📊 TF-IDF and cosine similarity ranking.
- 🎨 Interactive Streamlit interface with ranked results.
- 🧪 Search evaluation using precision, recall, and average precision.

## ⚙️ How It Works

1. **Discover** — DDGS finds topic-specific educational seed pages.
2. **Crawl** — A bounded crawler follows links on the same approved hostname.
3. **Scrape** — BeautifulSoup extracts readable page content and PDF links.
4. **Extract** — PDF text is extracted page by page using pypdf.
5. **Preprocess** — Tokenization, stop-word removal, POS tagging, and lemmatization normalize the text.
6. **Index** — An inverted index stores term postings and document frequencies.
7. **Retrieve & Rank** — Boolean matching and TF-IDF cosine similarity rank relevant results.
8. **Display** — The interface shows results with relevance scores, excerpts, and source links.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Frontend | Streamlit |
| Search Discovery | DDGS |
| Web Scraping | BeautifulSoup |
| PDF Processing | pypdf |
| NLP | NLTK & WordNet |
| Retrieval | Inverted Index, TF-IDF |
| Evaluation | Precision, Recall, Average Precision |

## 🚀 Getting Started

### Prerequisites

- Python 3.10, 3.11, or 3.12
- Internet connection
- Git (optional, for cloning the repository)

### Installation

Clone the repository:

```bash
git clone https://github.com/JomanaSobhy-Hub/Edu-Search-Engine.git
cd Edu-Search-Engine
```

Install the dependencies:

```bash
py -m pip install -r requirements.txt
```

Run the application:

```bash
py -m streamlit run app.py
```

Open the local URL displayed in your terminal.

## 📂 Project Structure

```text
Edu-Search-Engine/
│
├── app.py
├── collector.py
├── loader.py
├── preprocessing.py
├── indexer.py
├── evaluate.py
├── requirements.txt
├── evaluation/
│   └── relevance.json
├── voice_search/
│   └── index.html
└── .streamlit/
    └── config.toml
```

## 🔎 Search Capabilities

| Search Mode | Description |
|---|---|
| OR | Matches any query term |
| AND | Requires all query terms |
| NOT | Excludes specified terms |
| Synonyms | Expands queries using WordNet |

## 📈 Evaluation

Add human relevance labels to `evaluation/relevance.json`, then run:

```bash
py evaluate.py
```

The evaluation measures precision, recall, and average precision.

## ⚠️ Limitations

- The crawler is focused, not a full-web crawler.
- Each search is limited to 20 HTML requests and eight new PDFs.
- Search results depend on seed discovery and site accessibility.
- Scanned PDFs require OCR before text extraction.
- Cloud storage may be temporary after deployment.

## 👥 Team Workflow

The project is divided into five main areas:

1. Seed discovery and crawler policy.
2. HTML scraping and PDF extraction.
3. Text preprocessing and normalization.
4. Indexing, Boolean retrieval, and ranking.
5. User interface, evaluation, deployment, and documentation.

## 📜 Responsible Use

Collect only public educational resources you are permitted to access. Respect robots.txt, crawl delays, and source attribution.

---
### ↪️ You can try it: https://edu-search-engine-j9ayblfgmfsusdhejjddcj.streamlit.app/
<p align="center">
  <b>Educational Search Engine — Information Retrieval Project</b>
</p>
