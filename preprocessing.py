"""Tokenization and consistent English lemmatization for documents and queries."""
from __future__ import annotations

import re
from functools import lru_cache

import nltk
from nltk.stem import WordNetLemmatizer

_STOP_WORDS = set("""
a an the and or but if then else when at by for from in into of on to with as is are was were be been being
this that these those it its we you they them their our your he she his her not no do does did have has had
what which who whom where why how about after before between through during each few more most other some such
""".split())
_ARABIC_STOP_WORDS = set("في من على إلى عن ان أن أو و مع هذا هذه ذلك التي الذي هو هي كان تكون".split())
_TOKEN = re.compile(r"[^\W_]+", flags=re.UNICODE)
_LEMMATIZER = WordNetLemmatizer()
_NLTK_READY = False


def _ensure_nltk_data() -> None:
    """Install the small NLTK language resources once, on first English search."""
    global _NLTK_READY
    if _NLTK_READY:
        return
    resources = (
        ("corpora/wordnet", "wordnet"),
        ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
    )
    for resource_path, package in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            if not nltk.download(package, quiet=True):
                raise RuntimeError(
                    f"Could not download NLTK resource '{package}'. Connect to the internet and search again."
                )
    _NLTK_READY = True


@lru_cache(maxsize=50000)
def _lemma(word: str, pos: str) -> str:
    return _LEMMATIZER.lemmatize(word, pos=pos)


def normalize_tokens(text: str) -> list[str]:
    terms = []
    english = []
    for token in _TOKEN.findall(text.casefold()):
        if token in _STOP_WORDS or token in _ARABIC_STOP_WORDS or len(token) < 2:
            continue
        if token.isascii() and token.isalpha():
            english.append(token)
        else:
            terms.append(token)

    if english:
        _ensure_nltk_data()
        tagged = nltk.pos_tag(english)
        pos_map = {"J": "a", "V": "v", "R": "r"}
        terms.extend(_lemma(word, pos_map.get(tag[:1], "n")) for word, tag in tagged)
    return terms

def query_expansions(query_terms: list[str], vocabulary: set[str], limit_per_term: int = 3) -> list[list[str]]:
    """Return each query term plus up to a few single-word WordNet synonyms in the index."""
    if not query_terms:
        return []
    _ensure_nltk_data()
    from nltk.corpus import wordnet

    groups = []
    pos_map = {"a": "a", "s": "a", "v": "v", "r": "r", "n": "n"}
    for term in query_terms:
        alternatives = [term]
        seen = {term}
        for synset in wordnet.synsets(term)[:4]:
            pos = pos_map.get(synset.pos(), "n")
            for lemma_name in synset.lemma_names():
                if "_" in lemma_name or not lemma_name.isascii() or not lemma_name.isalpha():
                    continue
                candidate = _lemma(lemma_name.casefold(), pos)
                if (candidate != term and candidate in vocabulary and candidate not in seen
                        and candidate not in _STOP_WORDS and len(candidate) > 1):
                    alternatives.append(candidate)
                    seen.add(candidate)
                    if len(alternatives) >= limit_per_term + 1:
                        break
            if len(alternatives) >= limit_per_term + 1:
                break
        groups.append(alternatives)
    return groups
