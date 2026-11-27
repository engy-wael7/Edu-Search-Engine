"""Evaluate labeled queries in evaluation/relevance.json."""
import json
from pathlib import Path

from indexer import build_index, retrieval_metrics, search
from loader import load_documents

ROOT = Path(__file__).parent


def main() -> None:
    documents = load_documents()
    index = build_index(documents)
    labels = json.loads((ROOT / "evaluation" / "relevance.json").read_text(encoding="utf-8"))
    all_metrics = []
    for item in labels["queries"]:
        relevant = set(item.get("relevant_doc_ids", []))
        if not relevant:
            print(f"SKIP {item['query']}: add relevant page IDs after reviewing search results.")
            continue
        results = search(index, documents, item["query"], item.get("operator", "AND"),
                         item.get("exclude", ""), 10)
        metrics = retrieval_metrics(relevant, [result["doc_id"] for result in results])
        all_metrics.append(metrics)
        print(item["query"], metrics)
    if all_metrics:
        for name in ("precision", "recall", "average_precision"):
            average = sum(row[name] for row in all_metrics) / len(all_metrics)
            print(f"Mean {name}: {average:.3f}")
    else:
        print("No queries evaluated yet; add at least one non-empty relevance judgment.")


if __name__ == "__main__":
    main()
