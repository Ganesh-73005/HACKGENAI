import os
import re
import json
import faiss
import numpy as np
import torch
import streamlit as st
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter


st.title("Script Similarity Finder")


device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)


index = faiss.read_index("text_chunks_faiss_300.index")
with open("chunk_metadata_300.json", "r") as f:
    metadata = json.load(f)


splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "."],
    chunk_size=300,
    chunk_overlap=50,
)

def is_generic(text):
    
    return (
        len(text.strip()) < 30 or
        re.match(r"^(INT\.|EXT\.|CUT TO|FADE IN|FADE OUT)", text.strip(), re.I)
    )

def find_most_similar_chunk(input_text):
    input_chunks = splitter.split_text(input_text)
    input_embeddings = model.encode(input_chunks, convert_to_numpy=True)

    best_match = None
    best_score = float('inf')
    best_input_chunk = ""

    for idx, emb in enumerate(input_embeddings):
        chunk = input_chunks[idx]
        if is_generic(chunk):
            continue

        D, I = index.search(np.array([emb]), k=1)
        dist = D[0][0]
        i = I[0][0]

        if dist < 1.0 and dist < best_score:
            match_chunk = chunk
            matched_meta = metadata[i]
            best_score = dist
            best_match = matched_meta
            best_input_chunk = match_chunk

    return best_match, best_input_chunk, best_score


uploaded_file = st.file_uploader("📂 Upload a script file (.txt)", type=["txt"])

if uploaded_file:
    input_text = uploaded_file.read().decode("utf-8-sig", errors="ignore")

    with st.spinner("Searching for similar scenes..."):
        match, chunk_text, score = find_most_similar_chunk(input_text)

    if match:
        st.success("🎯 Closest Match Found")
        st.markdown(f"**Matched File:** `{match['source']}`")
        st.markdown(f"**Chunk Type:** `{match['chunk_type']}`")
        st.markdown(f"**Chunk ID:** `{match['chunk_id']}`")
        st.markdown(f"**Distance Score:** `{score:.4f}`")

        st.markdown("---")
        st.markdown("### 📌 Matched Snippet")
        st.code(chunk_text.strip())
    else:
        st.warning("No similar chunks found with meaningful content.")
