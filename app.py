# # from __future__ import annotations

# # import html
# # import re
# # import streamlit as st

# # from collector import crawl_and_scrape
# # from indexer import build_index, search
# # from loader import load_documents

# # def highlighted_snippet(text: str, query: str, width: int = 420) -> str:
# #     terms = re.findall(r"[^\W_]+", query, flags=re.UNICODE)
# #     folded = text.casefold()
# #     hits = [folded.find(term.casefold()) for term in terms if folded.find(term.casefold()) >= 0]
# #     start = max(min(hits) - 80, 0) if hits else 0
# #     excerpt = text[start:start + width]
# #     safe = html.escape(excerpt)
# #     for term in terms:
# #         safe_term = html.escape(term)
# #         safe = re.sub(rf"({re.escape(safe_term)})", r"<mark>\1</mark>", safe, flags=re.IGNORECASE)
# #     return ("… " if start else "") + safe + (" …" if start + width < len(text) else "")

# # st.set_page_config(page_title="Educational Search Engine", page_icon="📚", layout="wide")
# # st.title("📚 Educational Search Engine")
# # st.write("Search a growing collection of educational PDFs gathered from open academic sources.")

# # with st.sidebar:
# #     st.header("Search options")
# #     max_results = st.slider("Number of results", 1, 20, 10)
# #     operator = st.radio("Match query terms", ["AND", "OR"], index=1, horizontal=True,
# #                         help="OR (default) accepts any query term; AND requires every term.")
# #     expand_synonyms = st.checkbox("Include English synonyms", value=True,
# #                                  help="Adds matching WordNet synonyms found in the indexed collection.")
# #     excluded = st.text_input("Exclude terms (NOT)", placeholder="beginner, survey")
# #     st.caption("Sources: university domains, MIT OpenCourseWare, OpenStax, and arXiv.")

# # query = st.text_input("What educational topic are you looking for?",
# #                       placeholder="Machine Learning, Database, Neural Networks…")
# # if st.button("Search", type="primary"):
# #     if not query.strip():
# #         st.info("Enter a topic to search.")
# #     else:
# #         try:
# #             with st.spinner("Crawling educational sites, scraping pages, collecting PDFs, and building the index…"):
# #                 newly_collected = crawl_and_scrape(query.strip(), page_limit=20, pdf_limit=8)
# #                 documents = load_documents()
# #                 index = build_index(documents)
# #                 results = search(index, documents, query, operator, excluded, max_results, expand_synonyms)
# #         except Exception as exc:
# #             st.error("The collection or search index could not be built.")
# #             st.caption(f"Details: {exc}")
# #             newly_collected, documents, index, results = [], [], {"document_count": 0, "vocabulary_size": 0}, []

# #         if newly_collected:
# #             st.success(f"Added {len(newly_collected)} new educational source(s) to the local collection.")
# #         if not documents:
# #             st.warning("No readable educational pages or PDFs are in the collection yet. Check your internet connection and try another topic.")
# #         else:
# #             st.caption(f"Indexed {index['document_count']} source document(s) · {index['vocabulary_size']} unique terms")
# #             if not results:
# #                 st.info("No matches in the indexed documents. Try OR instead of AND, or change the search terms.")
# #             else:
# #                 st.subheader(f"Ranked results ({len(results)})")
# #                 for rank, result in enumerate(results, 1):
# #                     st.markdown(f"**{rank}. {result['title']}**")
# #                     location = "Web page" if result.get("kind") == "web" else f"Page {result['page']}"
# #                     st.caption(f"Relevance: {result['score'] * 100:.1f}% · {location} · {result['source']}")
# #                     if result.get("url"):
# #                         link_label = "Open source PDF" if result.get("kind") == "pdf" else "Open source page"
# #                         st.markdown(f"[{link_label}]({result['url']})")
# #                     st.markdown(highlighted_snippet(result["text"], query), unsafe_allow_html=True)
# #                     st.divider()

# # st.caption("Pipeline: discover seeds → crawl trusted educational sites → scrape pages and PDFs → extract → normalize → inverted index → Boolean filtering → TF-IDF/cosine ranking.")




# from __future__ import annotations

# import base64
# import html
# import re
# from pathlib import Path

# import streamlit as st

# from collector import collect_pdfs
# from indexer import build_index, search
# from loader import load_documents


# # =========================
# # Page configuration
# # =========================

# st.set_page_config(
#     page_title="EduSearch | Educational Search Engine",
#     page_icon="📚",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )


# # =========================
# # Background image
# # =========================

# image_path = Path(__file__).parent / "background.jpg"

# background_image = ""

# if image_path.exists():
#     image_data = base64.b64encode(
#         image_path.read_bytes()
#     ).decode("utf-8")

#     background_image = (
#         f", url('data:image/jpeg;base64,{image_data}')"
#     )


# # =========================
# # Interface design
# # =========================

# st.markdown(
#     f"""
#     <style>
#     .stApp {{
#         background-color: #071521;
#         background-image:
#             linear-gradient(
#                 135deg,
#                 rgba(4, 15, 26, 0.82),
#                 rgba(7, 29, 39, 0.88)
#             )
#             {background_image};
#         background-size: cover;
#         background-position: center;
#         background-attachment: fixed;
#     }}

#     [data-testid="stHeader"] {{
#         background: transparent;
#     }}

#     [data-testid="stSidebar"] {{
#         background: rgba(9, 25, 37, 0.97);
#         border-right: 1px solid #284858;
#     }}

#     .hero {{
#         text-align: center;
#         padding: 55px 20px 35px;
#         animation: fadeIn 0.8s ease-out;
#     }}

#     .hero-label {{
#         color: #80e6c7;
#         font-size: 13px;
#         font-weight: 700;
#         letter-spacing: 3px;
#     }}

#     .hero h1 {{
#         color: #f1fffb;
#         font-size: clamp(38px, 5vw, 64px);
#         letter-spacing: -2px;
#         margin: 12px 0;
#     }}

#     .hero p {{
#         color: #c5dce2;
#         font-size: 17px;
#         line-height: 1.7;
#         margin: 0;
#     }}

#     [data-testid="stTextInput"] input {{
#         min-height: 52px;
#         border-radius: 14px;
#         border: 1px solid #477180;
#         background: #102838;
#         color: #f4fffc;
#     }}

#     [data-testid="stTextInput"] input:focus {{
#         border-color: #79e6c3;
#         box-shadow: 0 0 0 3px rgba(121, 230, 195, 0.2);
#     }}

#     .stButton > button,
#     .stFormSubmitButton > button {{
#         min-height: 46px;
#         border-radius: 12px;
#         border: 1px solid #76dfba;
#         background: #76dfba;
#         color: #09271e;
#         font-weight: 700;
#         transition: transform 0.2s, box-shadow 0.2s;
#     }}

#     .stButton > button:hover,
#     .stFormSubmitButton > button:hover {{
#         background: #a1f4d6;
#         color: #09271e;
#         transform: translateY(-2px);
#         box-shadow: 0 8px 24px rgba(118, 223, 186, 0.25);
#     }}

#     [data-testid="stMetric"] {{
#         background: rgba(13, 35, 49, 0.95);
#         border: 1px solid #315365;
#         border-radius: 15px;
#         padding: 15px;
#     }}

#     [data-testid="stMetricValue"] {{
#         color: #80e6c7;
#     }}

#     [data-testid="stVerticalBlockBorderWrapper"] {{
#         background: rgba(12, 32, 46, 0.96);
#         border: 1px solid #315365;
#         border-radius: 18px;
#         transition: transform 0.2s, border-color 0.2s;
#     }}

#     [data-testid="stVerticalBlockBorderWrapper"]:hover {{
#         border-color: #76dfba;
#         transform: translateY(-2px);
#     }}

#     mark {{
#         background: #a6f2d5;
#         color: #102c27;
#         border-radius: 4px;
#         padding: 1px 3px;
#     }}

#     @keyframes fadeIn {{
#         from {{
#             opacity: 0;
#             transform: translateY(15px);
#         }}
#         to {{
#             opacity: 1;
#             transform: translateY(0);
#         }}
#     }}

#     @media (prefers-reduced-motion: reduce) {{
#         *, *::before, *::after {{
#             animation: none !important;
#             transition: none !important;
#         }}
#     }}
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# # =========================
# # Highlight matched terms
# # =========================

# def highlighted_snippet(
#     text: str,
#     query: str,
#     width: int = 420,
# ) -> str:

#     terms = list(dict.fromkeys(
#         re.findall(r"[^\\W_]+", query, flags=re.UNICODE)
#     ))

#     pattern = (
#         re.compile(
#             "|".join(
#                 re.escape(term)
#                 for term in sorted(terms, key=len, reverse=True)
#             ),
#             flags=re.IGNORECASE,
#         )
#         if terms else None
#     )

#     first_hit = pattern.search(text) if pattern else None
#     start = max(first_hit.start() - 80, 0) if first_hit else 0
#     excerpt = text[start:start + width]

#     if not pattern:
#         safe = html.escape(excerpt)
#     else:
#         parts = []
#         last = 0

#         for match in pattern.finditer(excerpt):
#             parts.append(
#                 html.escape(excerpt[last:match.start()])
#             )
#             parts.append(
#                 "<mark>"
#                 + html.escape(match.group())
#                 + "</mark>"
#             )
#             last = match.end()

#         parts.append(html.escape(excerpt[last:]))
#         safe = "".join(parts)

#     return (
#         ("… " if start else "")
#         + safe
#         + (" …" if start + width < len(text) else "")
#     )


# # =========================
# # Sidebar
# # =========================

# with st.sidebar:
#     st.header("⚙️ Search options")

#     max_results = st.slider(
#         "Number of results",
#         1,
#         20,
#         10,
#     )

#     operator = st.radio(
#         "Match query terms",
#         ["AND", "OR"],
#         horizontal=True,
#         help="AND requires every query term; OR accepts any term.",
#     )

#     excluded = st.text_input(
#         "Exclude terms (NOT)",
#         placeholder="beginner, survey",
#     )

#     st.divider()

#     st.caption(
#         "Sources: university domains, MIT OpenCourseWare, "
#         "OpenStax, and arXiv."
#     )

#     st.caption(
#         "Pipeline: collect → extract → normalize → "
#         "inverted index → Boolean filtering → TF-IDF ranking."
#     )


# # =========================
# # Hero section
# # =========================

# st.markdown(
#     """
#     <section class="hero">
#         <div class="hero-label">ACADEMIC DISCOVERY</div>
#         <h1>📚 EduSearch</h1>
#         <p>
#             Search educational PDFs and discover
#             relevant academic resources.
#         </p>
#     </section>
#     """,
#     unsafe_allow_html=True,
# )


# # =========================
# # Centered search bar
# # =========================
# st.markdown("""
# <style>
# /* لون السؤال */
# div[data-testid="stTextInput"] label,
# div[data-testid="stTextInput"] label p {
#      color: #c5dce2 !important;
# }

# /* لون الكلام اللي بتكتبيه */
# div[data-testid="stTextInput"] input {
#     color: white !important;

#     background-color: rgba(0, 0, 0, 0.35) !important;
# }

# /* لون النص الإرشادي */
# div[data-testid="stTextInput"] input::placeholder {
#     color: rgba(255, 255, 255, 0.75) !important;
     
# }
# </style>
# """, unsafe_allow_html=True)

# left, center, right = st.columns([1, 3, 1])

# with center:
#     with st.form("search_form"):
#         query = st.text_input(
#             "What educational topic are you looking for?",
#             placeholder="Machine Learning, Database, Neural Networks…",
#         )

#         search_clicked = st.form_submit_button(
#             "📚 Search documents",
#             type="primary",
#             use_container_width=True,
#         )


# # =========================
# # Search and indexing
# # =========================

# if search_clicked:
#     if not query.strip():
#         st.info("Enter a topic to search.")

#     else:
#         try:
#             st.markdown("""
# <style>
# div[data-testid="stSpinner"] p {
#     color: #c5dce2 !important;
# }
# </style>
# """, unsafe_allow_html=True)
#             with st.spinner(
#                 "Collecting educational PDFs and building the index…"
#             ):
#                 newly_collected = collect_pdfs(
#                     query.strip(),
#                     limit=8,
#                 )
#                 st.markdown("""
# <style>
# /* Results background */
# .st-key-results_area {
#     background-color: #ffffff !important;
#     color: #111111 !important;
#     padding: 28px !important;
#     border-radius: 20px !important;
#     margin-top: 20px;
# }

# /* All text inside results */
# .st-key-results_area h1,
# .st-key-results_area h2,
# .st-key-results_area h3,
# .st-key-results_area p,
# .st-key-results_area label,
# .st-key-results_area [data-testid="stMetricLabel"],
# .st-key-results_area [data-testid="stMetricValue"],
# .st-key-results_area [data-testid="stCaptionContainer"] {
#     color: #111111 !important;
# }

# /* Individual result cards */
# .st-key-results_area [data-testid="stVerticalBlockBorderWrapper"] {
#     background-color: #ffffff !important;
#     border: 1px solid #dce4e8 !important;
#     border-radius: 14px !important;
#     padding: 16px !important;
# }

# /* Highlighted search words */
# .st-key-results_area mark {
#     background-color: #a8eee0 !important;
#     color: #103b3b !important;
#     padding: 2px 5px;
#     border-radius: 5px;
# }

# /* Score color */
# .st-key-results_area [data-testid="stMetricValue"] {
#     color: #087f80 !important;
# }
# </style>
# """, unsafe_allow_html=True)

#                 documents = load_documents()
#                 index = build_index(documents)

#                 results = search(
#                     index,
#                     documents,
#                     query,
#                     operator,
#                     excluded,
#                     max_results,
#                 )

#             st.session_state["search_data"] = {
#                 "query": query,
#                 "results": results,
#                 "documents": documents,
#                 "index": index,
#                 "new_count": len(newly_collected),
#                 "operator": operator,
#             }

#         except Exception as exc:
#             st.session_state.pop("search_data", None)
#             st.error("The collection or search index could not be built.")
#             st.caption(f"Details: {exc}")


# # # =========================
# # # Results dashboard
# # # =========================

# # if "search_data" in st.session_state:
# #     data = st.session_state["search_data"]

# #     results = data["results"]
# #     documents = data["documents"]
# #     index = data["index"]
# #     searched_query = data["query"]

# #     if data["new_count"]:
# #         st.success(
# #             f"Added {data['new_count']} new PDF document(s) "
# #             "to the local collection."
# #         )

# #     if not documents:
# #         st.warning(
# #             "No readable educational PDFs were found. "
# #             "Check your internet connection and try again."
# #         )

# #     else:
# #         relevant_docs = {
# #             (
# #                 str(result.get("url") or ""),
# #                 str(result.get("source") or ""),
# #                 str(result.get("title") or ""),
# #             )
# #             for result in results
# #         }

# #         st.subheader(f"Results for: {searched_query}")

# #         c1, c2, c3 = st.columns(3)

# #         c1.metric(
# #             "Relevant documents",
# #             len(relevant_docs),
# #         )

# #         c2.metric(
# #             "Matched pages",
# #             len(results),
# #         )

# #         c3.metric(
# #             "Indexed pages",
# #             index.get("document_count", 0),
# #         )

# #         st.caption(
# #             f"Indexed vocabulary: "
# #             f"{index.get('vocabulary_size', 0)} unique terms "
# #             f"· Match mode: {data['operator']}"
# #         )

# #         if not results:
# #             st.info(
# #                 "No matches found. Try OR instead of AND, "
# #                 "remove excluded terms, or change the query."
# #             )

# #         else:
# #             st.markdown("### Ranked results")

# #             for rank, result in enumerate(results, 1):
# #                 score = float(result.get("score") or 0)
# #                 percent = score * 100

# #                 title = result.get("title") or "Untitled document"
# #                 source = result.get("source") or "Unknown source"
# #                 page = result.get("page", "—")

# #                 with st.container(border=True):
# #                     left, right = st.columns([4, 1])

# #                     with left:
# #                         st.markdown(f"### {rank:02d} · {title}")
# #                         st.caption(f"Page {page} · {source}")

# #                     with right:
# #                         st.metric(
# #                             "Score",
# #                             f"{percent:.1f}%",
# #                         )

# #                     st.progress(
# #                         max(0.0, min(score, 1.0))
# #                     )

# #                     snippet = highlighted_snippet(
# #                         str(result.get("text") or ""),
# #                         searched_query,
# #                     )

# #                     st.markdown(
# #                         snippet,
# #                         unsafe_allow_html=True,
# #                     )

# #                     url = str(result.get("url") or "")

# #                     if url.startswith(("https://", "http://")):
# #                         st.link_button(
# #                             "Open source PDF",
# #                             url,
# #                         )

# st.markdown("""
# <style>
# /* Metric cards background */
# .st-key-results_area [data-testid="stMetric"] {
#     background-color: #7EE3B3 !important;
#     border: 1px solid #65c99a !important;
#     border-radius: 18px !important;
#     padding: 18px !important;
# }

# /* Metric labels and values */
# .st-key-results_area [data-testid="stMetric"] * {
#     color: #000000 !important;
# }

# /* Keep the result cards white */
# .st-key-results_area [data-testid="stVerticalBlockBorderWrapper"] {
#     background-color: #ffffff !important;
# }
# </style>
# """, unsafe_allow_html=True)

# # =========================
# # Results dashboard
# # =========================

# if "search_data" in st.session_state:

#     data = st.session_state["search_data"]

#     results = data["results"]
#     documents = data["documents"]
#     index = data["index"]
#     searched_query = data["query"]

#     with st.container(key="results_area"):

#         if data["new_count"]:
#             st.success(
#                 f"Added {data['new_count']} new PDF document(s) "
#                 "to the local collection."
#             )

#         if not documents:
#             st.warning(
#                 "No readable educational PDFs were found. "
#                 "Check your internet connection and try again."
#             )

#         else:
#             relevant_docs = {
#                 (
#                     str(result.get("url") or ""),
#                     str(result.get("source") or ""),
#                     str(result.get("title") or ""),
#                 )
#                 for result in results
#             }

#             st.subheader(f"Results for: {searched_query}")

#             c1, c2, c3 = st.columns(3)

#             c1.metric("Relevant documents", len(relevant_docs))
#             c2.metric("Matched pages", len(results))
#             c3.metric(
#                 "Indexed pages",
#                 index.get("document_count", 0)
#             )

#             st.caption(
#                 f"Indexed vocabulary: "
#                 f"{index.get('vocabulary_size', 0)} unique terms "
#                 f"· Match mode: {data['operator']}"
#             )

#             if not results:
#                 st.info(
#                     "No matches found. Try OR instead of AND, "
#                     "remove excluded terms, or change the query."
#                 )

#             else:
#                 st.markdown("### Ranked results")

#                 for rank, result in enumerate(results, 1):

#                     score = float(result.get("score") or 0)
#                     percent = score * 100

#                     title = result.get("title") or "Untitled document"
#                     source = result.get("source") or "Unknown source"
#                     page = result.get("page", "—")

#                     with st.container(border=True):

#                         left, right = st.columns([4, 1])

#                         with left:
#                             st.markdown(f"### {rank:02d} · {title}")
#                             st.caption(f"Page {page} · {source}")

#                         with right:
#                             st.metric("Score", f"{percent:.1f}%")

#                         st.progress(
#                             max(0.0, min(score, 1.0))
#                         )

#                         snippet = highlighted_snippet(
#                             str(result.get("text") or ""),
#                             searched_query,
#                         )

#                         st.markdown(
#                             snippet,
#                             unsafe_allow_html=True,
#                         )

#                         url = str(result.get("url") or "")

#                         if url.startswith(("https://", "http://")):
#                             st.link_button("Open source PDF", url)








# old




# from __future__ import annotations

# import base64
# import html
# import re
# from pathlib import Path

# import streamlit as st

# from collector import collect_pdfs
# from indexer import build_index, search
# from loader import load_documents


# # =========================
# # Page configuration
# # =========================

# st.set_page_config(
#     page_title="EduSearch | Educational Search Engine",
#     page_icon="📚",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )


# # =========================
# # Dark / Light mode
# # =========================

# if "dark_mode" not in st.session_state:
#     st.session_state.dark_mode = True

# top_left, top_right = st.columns([5, 1])

# with top_right:
#     dark_mode = st.toggle(
#         "🌙 Dark mode",
#         key="dark_mode",
#     )

# if dark_mode:
#     overlay = "rgba(4, 15, 26, 0.82)"
#     page_bg = "#071521"
#     text_color = "#f1fffb"
#     input_bg = "#102838"
#     sidebar_bg = "#091925"
#     results_bg = "#102838"
#     card_bg = "#173444"
#     result_text = "#f1fffb"
# else:
#     overlay = "rgba(255, 255, 255, 0.88)"
#     page_bg = "#f5faf8"
#     text_color = "#111111"
#     input_bg = "#ffffff"
#     sidebar_bg = "#f5faf8"
#     results_bg = "#ffffff"
#     card_bg = "#ffffff"
#     result_text = "#111111"


# # =========================
# # Background image
# # =========================

# image_path = Path(__file__).parent / "background.jpg"
# background_image = ""

# if image_path.exists():
#     image_data = base64.b64encode(
#         image_path.read_bytes()
#     ).decode("utf-8")

#     background_image = (
#         f", url('data:image/jpeg;base64,{image_data}')"
#     )


# # =========================
# # Interface design
# # =========================

# st.markdown(
#     f"""
#     <style>
#     .stApp {{
#         background-color: {page_bg};
#         background-image:
#             linear-gradient({overlay}, {overlay})
#             {background_image};
#         background-size: cover;
#         background-position: center;
#         background-attachment: fixed;
#     }}

#     [data-testid="stHeader"] {{
#         background: transparent;
#     }}

#     [data-testid="stSidebar"] {{
#         background: {sidebar_bg};
#         border-right: 1px solid #477180;
#     }}

#     .hero {{
#         text-align: center;
#         padding: 35px 20px 25px;
#     }}

#     .hero-label {{
#         color: #16866b;
#         font-size: 13px;
#         font-weight: 700;
#         letter-spacing: 3px;
#     }}

#     .hero h1 {{
#         color: {text_color};
#         font-size: clamp(38px, 5vw, 64px);
#         letter-spacing: -2px;
#         margin: 12px 0;
#     }}

#     .hero p {{
#         color: {text_color};
#         font-size: 17px;
#         line-height: 1.7;
#     }}

#     /* Search input */
#     [data-testid="stTextInput"] input {{
#         min-height: 52px;
#         border-radius: 14px;
#         border: 1px solid #477180;
#         background: {input_bg} !important;
#         color: {text_color} !important;
#     }}

#     [data-testid="stTextInput"] label,
#     [data-testid="stTextInput"] label p {{
#         color: {text_color} !important;
#     }}

#     [data-testid="stTextInput"] input::placeholder {{
#         color: #78909c !important;
#     }}

#     /* Search button */
#     .stButton > button,
#     .stFormSubmitButton > button {{
#         min-height: 46px;
#         border-radius: 12px;
#         border: 1px solid #65c99a;
#         background: #7EE3B3;
#         color: #000000;
#         font-weight: 700;
#     }}

#     .stButton > button:hover,
#     .stFormSubmitButton > button:hover {{
#         background: #a1f4d6;
#         color: #000000;
#     }}

#     /* Results dashboard */
#     .st-key-results_area {{
#         background: {results_bg} !important;
#         color: {result_text} !important;
#         padding: 28px !important;
#         border-radius: 20px !important;
#         margin-top: 24px;
#     }}

#     .st-key-results_area h1,
#     .st-key-results_area h2,
#     .st-key-results_area h3,
#     .st-key-results_area p,
#     .st-key-results_area label,
#     .st-key-results_area [data-testid="stCaptionContainer"] {{
#         color: {result_text} !important;
#     }}

#     /* Result cards */
#     .st-key-results_area
#     [data-testid="stVerticalBlockBorderWrapper"] {{
#         background: {card_bg} !important;
#         border: 1px solid #8fb6ad !important;
#         border-radius: 16px !important;
#         padding: 16px !important;
#     }}

#     /* Metrics and score */
#     .st-key-results_area [data-testid="stMetric"] {{
#         background: #7EE3B3 !important;
#         border: 1px solid #65c99a !important;
#         border-radius: 16px !important;
#         padding: 18px !important;
#     }}

#     .st-key-results_area [data-testid="stMetric"] * {{
#         color: #000000 !important;
#     }}

#     /* Highlighted words */
#     .st-key-results_area mark {{
#         background: #7EE3B3 !important;
#         color: #000000 !important;
#         padding: 2px 5px;
#         border-radius: 5px;
#     }}

#     /* Spinner */
#     [data-testid="stSpinner"] p {{
#         color: {text_color} !important;
#     }}
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# # =========================
# # Highlight matched terms
# # =========================

# def highlighted_snippet(
#     text: str,
#     query: str,
#     width: int = 420,
# ) -> str:

#     terms = list(dict.fromkeys(
#         re.findall(r"[^\W_]+", query, flags=re.UNICODE)
#     ))

#     pattern = (
#         re.compile(
#             "|".join(
#                 re.escape(term)
#                 for term in sorted(terms, key=len, reverse=True)
#             ),
#             flags=re.IGNORECASE,
#         )
#         if terms else None
#     )

#     first_hit = pattern.search(text) if pattern else None
#     start = max(first_hit.start() - 80, 0) if first_hit else 0
#     excerpt = text[start:start + width]

#     if not pattern:
#         safe = html.escape(excerpt)
#     else:
#         parts = []
#         last = 0

#         for match in pattern.finditer(excerpt):
#             parts.append(
#                 html.escape(excerpt[last:match.start()])
#             )
#             parts.append(
#                 "<mark>"
#                 + html.escape(match.group())
#                 + "</mark>"
#             )
#             last = match.end()

#         parts.append(html.escape(excerpt[last:]))
#         safe = "".join(parts)

#     return (
#         ("… " if start else "")
#         + safe
#         + (" …" if start + width < len(text) else "")
#     )


# # =========================
# # Sidebar
# # =========================

# with st.sidebar:
#     st.header("⚙️ Search options")

#     max_results = st.slider(
#         "Number of results",
#         1,
#         20,
#         10,
#     )

#     operator = st.radio(
#         "Match query terms",
#         ["AND", "OR"],
#         horizontal=True,
#     )

#     excluded = st.text_input(
#         "Exclude terms (NOT)",
#         placeholder="beginner, survey",
#     )

#     st.divider()

#     st.caption(
#         "Sources: university domains, MIT OpenCourseWare, "
#         "OpenStax, and arXiv."
#     )


# # =========================
# # Hero section
# # =========================

# st.markdown(
#     """
#     <section class="hero">
#         <div class="hero-label">ACADEMIC DISCOVERY</div>
#         <h1>📚 EduSearch</h1>
#         <p>
#             Search educational PDFs and discover
#             relevant academic resources.
#         </p>
#     </section>
#     """,
#     unsafe_allow_html=True,
# )


# # =========================
# # Centered search bar
# # =========================

# left, center, right = st.columns([1, 3, 1])

# with center:
#     with st.form("search_form"):
#         query = st.text_input(
#             "What educational topic are you looking for?",
#             placeholder="Machine Learning, Database, Neural Networks…",
#         )

#         search_clicked = st.form_submit_button(
#             "📚 Search documents",
#             type="primary",
#             use_container_width=True,
#         )


# # =========================
# # Search and indexing
# # =========================

# if search_clicked:
#     if not query.strip():
#         st.info("Enter a topic to search.")

#     else:
#         try:
#             with st.spinner(
#                 "Collecting educational PDFs and building the index…"
#             ):
#                 newly_collected = collect_pdfs(
#                     query.strip(),
#                     limit=8,
#                 )

#                 documents = load_documents()
#                 index = build_index(documents)

#                 results = search(
#                     index,
#                     documents,
#                     query,
#                     operator,
#                     excluded,
#                     max_results,
#                 )

#             st.session_state["search_data"] = {
#                 "query": query,
#                 "results": results,
#                 "documents": documents,
#                 "index": index,
#                 "new_count": len(newly_collected),
#                 "operator": operator,
#             }

#         except Exception as exc:
#             st.session_state.pop("search_data", None)
#             st.error(
#                 "The collection or search index could not be built."
#             )
#             st.caption(f"Details: {exc}")


# # =========================
# # Results dashboard
# # =========================

# if "search_data" in st.session_state:

#     data = st.session_state["search_data"]

#     results = data["results"]
#     documents = data["documents"]
#     index = data["index"]
#     searched_query = data["query"]

#     with st.container(key="results_area"):

#         if data["new_count"]:
#             st.success(
#                 f"Added {data['new_count']} new PDF document(s) "
#                 "to the local collection."
#             )

#         if not documents:
#             st.warning(
#                 "No readable educational PDFs were found. "
#                 "Check your internet connection and try again."
#             )

#         else:
#             relevant_docs = {
#                 (
#                     str(result.get("url") or ""),
#                     str(result.get("source") or ""),
#                     str(result.get("title") or ""),
#                 )
#                 for result in results
#             }

#             st.subheader(f"Results for: {searched_query}")

#             c1, c2, c3 = st.columns(3)

#             c1.metric(
#                 "Relevant documents",
#                 len(relevant_docs),
#             )

#             c2.metric(
#                 "Matched pages",
#                 len(results),
#             )

#             c3.metric(
#                 "Indexed pages",
#                 index.get("document_count", 0),
#             )

#             st.caption(
#                 f"Indexed vocabulary: "
#                 f"{index.get('vocabulary_size', 0)} unique terms "
#                 f"· Match mode: {data['operator']}"
#             )

#             if not results:
#                 st.info(
#                     "No matches found. Try OR instead of AND, "
#                     "remove excluded terms, or change the query."
#                 )

#             else:
#                 st.markdown("### Ranked results")

#                 for rank, result in enumerate(results, 1):

#                     score = float(result.get("score") or 0)
#                     percent = score * 100

#                     title = (
#                         result.get("title")
#                         or "Untitled document"
#                     )
#                     source = (
#                         result.get("source")
#                         or "Unknown source"
#                     )
#                     page = result.get("page", "—")

#                     with st.container(border=True):

#                         left, right = st.columns([4, 1])

#                         with left:
#                             st.markdown(
#                                 f"### {rank:02d} · {title}"
#                             )
#                             st.caption(
#                                 f"Page {page} · {source}"
#                             )

#                         with right:
#                             st.metric(
#                                 "Score",
#                                 f"{percent:.1f}%",
#                             )

#                         st.progress(
#                             max(0.0, min(score, 1.0))
#                         )

#                         snippet = highlighted_snippet(
#                             str(result.get("text") or ""),
#                             searched_query,
#                         )

#                         st.markdown(
#                             snippet,
#                             unsafe_allow_html=True,
#                         )

#                         url = str(result.get("url") or "")

#                         if url.startswith(
#                             ("https://", "http://")
#                         ):
#                             st.link_button(
#                                 "Open source PDF",
#                                 url,
#                             )

# new

from __future__ import annotations

import base64
import html
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from collector import collect_pdfs
from indexer import build_index, search
from loader import load_documents


# =========================
# Page configuration
# =========================

st.set_page_config(
    page_title="EduSearch | Educational Search Engine",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "voice_query" not in st.session_state:
    st.session_state.voice_query = ""


# =========================
# Theme
# =========================

left, right = st.columns([5, 1])

with right:
    dark_mode = st.toggle(
        "🌙 Dark mode",
        key="dark_mode",
    )

if dark_mode:
    page_bg = "#071521"
    text_color = "#f1fffb"
    sidebar_bg = "#091925"
    input_bg = "#102838"
    results_bg = "#102838"
    overlay = "rgba(4, 15, 26, 0.82)"
else:
    page_bg = "#f5faf8"
    text_color = "#111111"
    sidebar_bg = "#f5faf8"
    input_bg = "#ffffff"
    results_bg = "#ffffff"
    overlay = "rgba(255, 255, 255, 0.88)"


# =========================
# Background
# =========================

image_path = Path(__file__).parent / "background.jpg"
background_image = ""

if image_path.exists():
    image_data = base64.b64encode(
        image_path.read_bytes()
    ).decode("utf-8")

    background_image = (
        f", url('data:image/jpeg;base64,{image_data}')"
    )


# =========================
# CSS
# =========================

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {page_bg};
        background-image:
            linear-gradient({overlay}, {overlay})
            {background_image};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stSidebar"] {{
        background: {sidebar_bg};
    }}

    [data-testid="stSidebar"] *,
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] p,
    [data-testid="stMain"] label {{
        color: {text_color};
    }}

    .hero {{
        text-align: center;
        padding: 30px 15px 20px;
    }}

    .hero-label {{
        color: #36b995;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 3px;
    }}

    .hero h1 {{
        color: {text_color};
        font-size: clamp(38px, 5vw, 64px);
        margin: 12px 0;
    }}

    .hero p {{
        color: {text_color};
        font-size: 17px;
        line-height: 1.7;
    }}

    .st-key-results_area {{
        background: {results_bg} !important;
        color: {text_color} !important;
        padding: 24px !important;
        border-radius: 20px;
        margin-top: 24px;
    }}

    .st-key-results_area h1,
    .st-key-results_area h2,
    .st-key-results_area h3,
    .st-key-results_area p,
    .st-key-results_area label,
    .st-key-results_area [data-testid="stCaptionContainer"] {{
        color: {text_color} !important;
    }}

    .st-key-results_area [data-testid="stVerticalBlockBorderWrapper"] {{
        background: {results_bg} !important;
        border: 1px solid #8fb6ad !important;
        border-radius: 16px;
        padding: 14px;
    }}

    [data-testid="stMetric"] {{
        background: #7EE3B3 !important;
        border: 1px solid #65c99a !important;
        border-radius: 16px !important;
        padding: 18px !important;
    }}

    [data-testid="stMetric"] * {{
        color: #000000 !important;
    }}

    .st-key-results_area mark {{
        background: #7EE3B3 !important;
        color: #000000 !important;
        padding: 2px 5px;
        border-radius: 5px;
    }}

    .stButton > button {{
        background: #7EE3B3;
        color: #000000;
        border: 1px solid #65c99a;
        border-radius: 24px;
        min-height: 46px;
        font-weight: 700;
    }}

    .stButton > button:hover {{
        background: #a1f4d6;
        color: #000000;
    }}

    [data-testid="stSpinner"] p {{
        color: {text_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# Highlight matched terms
# =========================

def highlighted_snippet(
    text: str,
    query: str,
    width: int = 420,
) -> str:

    terms = list(dict.fromkeys(
        re.findall(r"[^\W_]+", query, flags=re.UNICODE)
    ))

    pattern = (
        re.compile(
            "|".join(
                re.escape(term)
                for term in sorted(terms, key=len, reverse=True)
            ),
            flags=re.IGNORECASE,
        )
        if terms else None
    )

    first_hit = pattern.search(text) if pattern else None
    start = max(first_hit.start() - 80, 0) if first_hit else 0
    excerpt = text[start:start + width]

    if not pattern:
        safe = html.escape(excerpt)
    else:
        parts = []
        last = 0

        for match in pattern.finditer(excerpt):
            parts.append(html.escape(excerpt[last:match.start()]))
            parts.append(
                "<mark>" + html.escape(match.group()) + "</mark>"
            )
            last = match.end()

        parts.append(html.escape(excerpt[last:]))
        safe = "".join(parts)

    return (
        ("… " if start else "")
        + safe
        + (" …" if start + width < len(text) else "")
    )


# =========================
# Sidebar
# =========================

with st.sidebar:
    st.header("⚙️ Search options")

    max_results = st.slider(
        "Number of results",
        1,
        20,
        10,
    )

    operator = st.radio(
        "Match query terms",
        ["AND", "OR"],
        horizontal=True,
    )

    excluded = st.text_input(
        "Exclude terms (NOT)",
        placeholder="beginner, survey",
    )

    st.divider()
    st.caption(
        "Sources: university domains, MIT OpenCourseWare, "
        "OpenStax, and arXiv."
    )


# =========================
# Hero section
# =========================

st.markdown(
    """
    <section class="hero">
        <div class="hero-label">ACADEMIC DISCOVERY</div>
        <h1>📚 EduSearch</h1>
        <p>
            Search educational PDFs and discover
            relevant academic resources.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# =========================
# Voice search component
# =========================

voice_search = components.declare_component(
    "voice_search",
    path=str(Path(__file__).parent / "voice_search"),
)

left, center, right = st.columns([1, 3, 1])

with center:
    voice_value = voice_search(
        dark=dark_mode,
        default=None,
        key="voice_search",
    )

    if isinstance(voice_value, dict):
        st.session_state.voice_query = str(
            voice_value.get("query", "")
        )

    query = st.session_state.voice_query

    search_clicked = st.button(
        "📚 Search documents",
        type="primary",
        use_container_width=True,
    )


# =========================
# Search and indexing
# =========================

if search_clicked:
    if not query.strip():
        st.info("Enter a topic or use the microphone.")
    else:
        try:
            with st.spinner(
                "Collecting educational PDFs and building the index…"
            ):
                newly_collected = collect_pdfs(
                    query.strip(),
                    limit=8,
                )

                documents = load_documents()
                index = build_index(documents)

                results = search(
                    index,
                    documents,
                    query,
                    operator,
                    excluded,
                    max_results,
                )

            st.session_state.search_data = {
                "query": query,
                "results": results,
                "documents": documents,
                "index": index,
                "new_count": len(newly_collected),
                "operator": operator,
            }

        except Exception as exc:
            st.error("The collection or search index could not be built.")
            st.caption(f"Details: {exc}")


# =========================
# Results dashboard
# =========================

if "search_data" in st.session_state:
    data = st.session_state.search_data

    results = data["results"]
    documents = data["documents"]
    index = data["index"]
    searched_query = data["query"]

    with st.container(key="results_area"):
        if data["new_count"]:
            st.success(
                f"Added {data['new_count']} new PDF document(s) "
                "to the local collection."
            )

        if not documents:
            st.warning("No readable educational PDFs were found.")
        else:
            relevant_docs = {
                (
                    str(result.get("url") or ""),
                    str(result.get("source") or ""),
                    str(result.get("title") or ""),
                )
                for result in results
            }

            st.subheader(f"Results for: {searched_query}")

            c1, c2, c3 = st.columns(3)

            c1.metric("Relevant documents", len(relevant_docs))
            c2.metric("Matched pages", len(results))
            c3.metric(
                "Indexed pages",
                index.get("document_count", 0),
            )

            st.caption(
                f"Indexed vocabulary: "
                f"{index.get('vocabulary_size', 0)} unique terms "
                f"· Match mode: {data['operator']}"
            )

            if not results:
                st.info(
                    "No matches found. Try OR instead of AND "
                    "or change the query."
                )
            else:
                st.markdown("### Ranked results")

                for rank, result in enumerate(results, 1):
                    score = float(result.get("score") or 0)
                    percent = score * 100

                    title = result.get("title") or "Untitled document"
                    source = result.get("source") or "Unknown source"
                    page = result.get("page", "—")

                    with st.container(border=True):
                        left, right = st.columns([4, 1])

                        with left:
                            st.markdown(f"### {rank:02d} · {title}")
                            st.caption(f"Page {page} · {source}")

                        with right:
                            st.metric("Score", f"{percent:.1f}%")

                        st.progress(
                            max(0.0, min(score, 1.0))
                        )

                        snippet = highlighted_snippet(
                            str(result.get("text") or ""),
                            searched_query,
                        )

                        st.markdown(
                            snippet,
                            unsafe_allow_html=True,
                        )

                        url = str(result.get("url") or "")

                        if url.startswith(("https://", "http://")):
                            st.link_button("Open source PDF", url)