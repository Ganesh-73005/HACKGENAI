import os
import re
import json
import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Check for GPU

if torch.cuda.is_available():
    print("✅ GPU is available:", torch.cuda.get_device_name(0))
    device = "cuda"
else:
    print("❌ GPU is not available.")
    device = "cpu"
# Use a lighter model (e.g., all-MiniLM-L6-v2)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)

# Splitter
splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "."],
    chunk_size=300,  # Slightly larger for fuller context
    chunk_overlap=50,
)

# Paths
dataset = "C:\\Users\\GIRISHSAI RAJA\\Downloads\\Cinebro\\ds"
chunk_list = []
metadata = []

# --- PREPROCESS AND CHUNK EACH FILE ---
def preprocess_and_chunk(file_path, file_name):
    dialogues = []
    descriptions = []

    with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        lines = f.readlines()

    current_block = []
    current_type = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r"^[A-Z][A-Z\s]*:", line):  # Detects dialogue
            if current_type != "dialogue" and current_block:
                descriptions.append("\n".join(current_block))
                current_block = []
            current_type = "dialogue"
            current_block.append(line)
        else:
            if current_type != "description" and current_block:
                dialogues.append("\n".join(current_block))
                current_block = []
            current_type = "description"
            current_block.append(line)

    # Save the last block
    if current_block:
        if current_type == "dialogue":
            dialogues.append("\n".join(current_block))
        else:
            descriptions.append("\n".join(current_block))

    # Chunk separately
    dialogue_chunks = splitter.split_text("\n\n".join(dialogues))
    description_chunks = splitter.split_text("\n\n".join(descriptions))

    # Add to master lists
    chunk_list.extend(dialogue_chunks)
    chunk_list.extend(description_chunks)

    film_name = re.sub(r'(_\d+)?\.txt$', '', file_name)

    metadata.extend([
        {"source": file_name, "chunk_type": "dialogue", "chunk_id": i}
        for i in range(len(dialogue_chunks))
    ] + [
        {"source": file_name, "chunk_type": "description", "chunk_id": i}
        for i in range(len(description_chunks))
    ])


# Loop through all dataset files
for file_name in os.listdir(dataset):
    if file_name.endswith(".txt"):
        file_path = os.path.join(dataset, file_name)
        preprocess_and_chunk(file_path, file_name)

# --- EMBEDDING AND INDEXING ---
print("🔄 Encoding all chunks...")
embeddings = model.encode(chunk_list, convert_to_numpy=True)
dim = embeddings.shape[1]

index = faiss.IndexFlatL2(dim)
index.add(embeddings)

# Save index and metadata
faiss.write_index(index, "text_chunks_faiss_300.index")
with open("chunk_metadata_300.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("✅ Indexing completed. Total chunks:", len(chunk_list))

# --- INPUT SCRIPT QUERY FUNCTION ---
def input_file(inputfile, splitter):
    index = faiss.read_index("text_chunks_faiss_300.index")
    with open("chunk_metadata_300.json", "r") as f:
        metadata = json.load(f)
    with open(inputfile, "r", encoding="utf-8-sig", errors="ignore") as f:
        input_text = f.read()

    input_chunks = splitter.split_text(input_text)
    input_embeddings = model.encode(input_chunks, convert_to_numpy=True)

    for idx, emb in enumerate(input_embeddings):
        D, I = index.search(np.array([emb]), k=1)
        distances = D[0]
        indices = I[0]

        for i, dist in zip(indices, distances):
            if dist < 1.0:
                print(f"\n🔍 Similarity found for input chunk #{idx}")
                print(f"Matched File: {metadata[i]['source']} | Chunk Type: {metadata[i]['chunk_type']} | Chunk ID: {metadata[i]['chunk_id']}")
                print(f"Distance Score: {dist:.4f}")
                print("\nMatched Input Snippet:")
                print("-" * 50)
                print(input_chunks[idx])
                print("-" * 50)


# --- RUN INPUT CHECK ---
input_file("inputs\input3.txt", splitter=splitter)
