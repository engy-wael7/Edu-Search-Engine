"""Inverted index, Boolean retrieval, and TF-IDF cosine ranking."""
from __future__ import annotations

import math
from collections import Counter, defaultdict

from preprocessing import normalize_tokens, query_expansions


def build_index(documents: list[dict]) -> dict:
    postings = defaultdict(dict)
    doc_tokens = {}
    doc_lengths = {}
    for index, document in enumerate(documents):
        tokens = normalize_tokens(document["text"])
        counts = Counter(tokens)
        doc_tokens[index] = counts
        doc_lengths[index] = max(len(tokens), 1)
        for term, frequency in counts.items():
            postings[term][index] = frequency
    posting_lists = dict(postings)
    return {
        "postings": posting_lists,
        "document_frequency": {term: len(posting) for term, posting in posting_lists.items()},
        "doc_tokens": doc_tokens,
        "doc_lengths": doc_lengths,
        "document_count": len(documents),
        "vocabulary_size": len(postings),
    }


def _intersect(left: list[int], right: list[int]) -> list[int]:
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] == right[j]:
            merged.append(left[i])
            i += 1
            j += 1
        elif left[i] < right[j]:
            i += 1
        else:
            j += 1
    return merged


def _union(left: list[int], right: list[int]) -> list[int]:
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] == right[j]:
            merged.append(left[i])
            i += 1
            j += 1
        elif left[i] < right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    return merged + left[i:] + right[j:]


def _difference(left: list[int], right: list[int]) -> list[int]:
    remaining = []
    i = j = 0
    while i < len(left):
        while j < len(right) and right[j] < left[i]:
            j += 1
        if j == len(right) or right[j] != left[i]:
            remaining.append(left[i])
        i += 1
    return remaining


def _candidates(index: dict, query_groups: list[list[str]], operator: str,
                excluded_terms: list[str]) -> set[int]:
    postings = index["postings"]
    group_lists = []
    for group in query_groups:
        alternatives = []
        for term in group:
            alternatives = _union(alternatives, sorted(postings.get(term, {})))
        group_lists.append(alternatives)
    if not group_lists:
        return set()
    candidates = group_lists[0]
    for posting_list in group_lists[1:]:
        candidates = _intersect(candidates, posting_list) if operator == "AND" else _union(candidates, posting_list)

    excluded = []
    for term in excluded_terms:
        excluded = _union(excluded, sorted(postings.get(term, {})))
    return set(_difference(candidates, excluded))


def search(index: dict, documents: list[dict], query: str, operator: str = "OR",
           exclude: str = "", limit: int = 10, expand_synonyms: bool = False) -> list[dict]:
    query_terms = normalize_tokens(query)
    excluded_terms = normalize_tokens(exclude)
    query_groups = query_expansions(query_terms, set(index["postings"])) if expand_synonyms else [[term] for term in query_terms]
    candidates = _candidates(index, query_groups, operator, excluded_terms)
    if not candidates:
        return []

    total_docs = max(index["document_count"], 1)
    query_counts = Counter(query_terms)

    def idf(term: str) -> float:
        df = index["document_frequency"].get(term, 0)
        if not df:
            return 0.0
        return math.log10((total_docs + 1) / (df + 1)) + 1.0

    query_vector = {term: (1 + math.log10(count)) * idf(term) for term, count in query_counts.items()}
    if expand_synonyms:
        for original, group in zip(query_terms, query_groups):
            original_weight = query_vector.get(original, idf(original))
            for synonym in group[1:]:
                query_vector[synonym] = max(query_vector.get(synonym, 0.0), original_weight * 0.35)
    query_norm = math.sqrt(sum(weight * weight for weight in query_vector.values())) or 1.0
    scored = []
    for doc_id in sorted(candidates):
        counts = index["doc_tokens"][doc_id]
        length = index["doc_lengths"][doc_id]
        doc_vector = {term: (1 + math.log10(count)) * idf(term) for term, count in counts.items()}
        doc_norm = math.sqrt(sum(weight * weight for weight in doc_vector.values())) or 1.0
        dot = sum(weight * doc_vector.get(term, 0.0) for term, weight in query_vector.items())
        score = dot / (query_norm * doc_norm)
        scored.append({**documents[doc_id], "score": score})
    # Results represent documents, not individual pages: keep only each PDF's best page.
    best_by_source = {}
    for item in scored:
        source_key = item.get("source") or item.get("doc_id")
        current = best_by_source.get(source_key)
        if current is None or item["score"] > current["score"]:
            best_by_source[source_key] = item
    return sorted(
        best_by_source.values(),
        key=lambda item: (-item["score"], item.get("title", "").casefold(), item.get("source", "")),
    )[:max(0, limit)]


def retrieval_metrics(relevant: set[str], retrieved: list[str]) -> dict[str, float]:
    """Precision, recall, and average precision for a manually judged query."""
    relevant_retrieved = [doc_id for doc_id in retrieved if doc_id in relevant]
    precision = len(relevant_retrieved) / len(retrieved) if retrieved else 0.0
    recall = len(relevant_retrieved) / len(relevant) if relevant else 0.0
    hits = 0
    precision_sum = 0.0
    for rank, doc_id in enumerate(retrieved, 1):
        if doc_id in relevant:
            hits += 1
            precision_sum += hits / rank
    average_precision = precision_sum / len(relevant) if relevant else 0.0
    return {"precision": precision, "recall": recall, "average_precision": average_precision}







