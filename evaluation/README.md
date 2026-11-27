# Evaluating search quality

After one or more searches have collected PDFs, open evaluation/relevance.json. For each query, copy relevant page IDs from the indexed results into relevant_doc_ids. Add 5–10 varied queries (including AND, OR, and exclusions), then run:

    py evaluate.py

The script reports precision, recall, and average precision per query and the mean of each metric. Relevance labels must be judged by a person; an empty list is only a template and does not represent a measured score.
