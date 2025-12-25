# src/rag_backend.py
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Setup Bedrock Client for Embeddings
# We use the 'titan-embed-text-v1' model to convert text to vectors
def get_bedrock_embeddings():
    return BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v1",
        region_name="us-east-1"
    )

# 2. Build the Vector Store (The "Knowledge Base")
def build_vector_store():
    print("🔄 Loading Policy Document...")
    
    # A. Load the Data
    loader = TextLoader("data/policy_2025.txt")
    documents = loader.load()
    
    # B. Split the Data (Chunking)
    # Why? We can't feed the whole book to the AI. We feed it relevant paragraphs.
    # Chunk size 1000 characters with 200 overlap ensures context isn't lost at the cut.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    docs = text_splitter.split_documents(documents)
    print(f"✅ Document split into {len(docs)} chunks.")
    
    # C. Embed and Store
    print("🧠 Generating Embeddings (Amazon Titan)...")
    embeddings = get_bedrock_embeddings()
    
    # Create the Vector Store using FAISS
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # D. Save to Disk (So we don't pay to re-embed every time)
    vectorstore.save_local("faiss_index_policy")
    print("✅ Vector Store saved successfully to 'faiss_index_policy'")
    
    return vectorstore

# 3. Search Function (To test it works)
def search_policy(query):
    embeddings = get_bedrock_embeddings()
    # Load the existing index
    new_vectorstore = FAISS.load_local(
        "faiss_index_policy", 
        embeddings
    #    allow_dangerous_deserialization=True # Trusted local source
    )
    
    results = new_vectorstore.similarity_search(query, k=6)
    return results

if __name__ == "__main__":
    # If we run this script directly, rebuild the database and test a query
    build_vector_store()
    
    # Test Run
    test_query = "What is the minimum credit score?"
    print(f"\n🔎 Testing Query: '{test_query}'")
    results = search_policy(test_query)
    
    print("\n--- Retrieved Context ---")
    for doc in results:
        print(doc.page_content)
        print("-------------------------")