# Educational Search Engine

A local Information Retrieval project for a growing collection of educational web pages and PDFs. It starts from topic-specific search results, then crawls a bounded set of links on the same approved educational site, scrapes readable page text, and downloads linked educational PDFs. The corpus grows automatically without manual uploads. It does not crawl the whole internet like Google.

## Crawling and scraping (the main collection stage)

- **Discover seeds:** DDGS finds a small set of starting pages for the topic on university, MIT OpenCourseWare, OpenStax, and arXiv domains.
- **Crawl:** a breadth-first crawler follows links only on the same hostname as each seed, up to two link levels, with a cap of 20 HTML requests per search.
- **Respect sites:** before requesting a page or PDF, the crawler checks `robots.txt`, uses a clear user agent, and waits at least the advertised crawl delay (minimum one second) between requests to a host.
- **Scrape:** BeautifulSoup removes navigation, scripts, forms, and other page chrome, then extracts the title and readable body text. It also discovers PDF links.
- **Collect files:** up to eight new PDFs per search are checked for approved host, size, and PDF signature before saving. HTML pages and PDFs are saved locally with source URLs.

This is the project's focused crawler, not a general web crawler: it can only find pages reachable from the search seeds, and the seed provider may return few results or block requests. The crawler keeps same-host traversal bounded to avoid wandering across the web.

## Search pipeline

1. **Crawl and scrape:** discover educational seeds, follow same-site links, extract page text, and find PDF links.
2. **Extract:** pypdf reads PDFs page by page; scraped HTML pages are indexed as individual documents.
3. **Preprocess:** Unicode tokenization and stop-word removal clean documents and queries; NLTK POS tagging and WordNet lemmatization normalize English terms consistently. The first English search downloads the required NLTK data once.
4. **Index:** a Python inverted index stores term postings and document frequency.
5. **Retrieve:** OR is the default; AND requires a match for each query term; NOT excludes exact terms. Optional WordNet synonyms can expand terms within the indexed vocabulary.
6. **Rank:** Log-TF × smoothed IDF weights and cosine similarity rank results. The best matching page from each PDF is shown to keep one large file from filling the list.
7. **Display:** Streamlit shows ranked sources, relevance score, page, excerpt, and a link to the original page or PDF.
8. **Evaluate:** add human relevance labels to `evaluation/relevance.json` and run `evaluate.py` for precision, recall, and average precision.
9. **Deploy:** the app can be deployed from a GitHub repository on Streamlit Community Cloud. Cloud storage is temporary, so the corpus may need to be collected again after a restart.

## Run locally

Python 3.10–3.12 is recommended. In PowerShell, open this folder and run:

    py -m pip install -r requirements.txt
    py -m streamlit run app.py

Internet access is needed for seed discovery, crawling, PDF downloads, and the first English search's NLTK data setup. Scanned image-only PDFs require OCR before their text can be indexed.

## Five-person split

1. Seed discovery, crawler limits, and site policy: `collector.py`
2. HTML/PDF scraping and extraction: `collector.py` and `loader.py`
3. Text normalization and lemmatization: `preprocessing.py`
4. Inverted index, Boolean search, and ranking: `indexer.py`
5. Streamlit interface, evaluation, deployment, and report: `app.py` and `evaluate.py`

Only collect public resources you are allowed to use. Keep source URLs and cite them in the project report.
