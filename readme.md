# 🏦 Commercial Loan Risk Assessment Agent

## 📋 Executive Summary
This project is an **Agentic AI System** designed to automate the initial risk assessment of commercial loan applications. Unlike standard chatbots, this system utilizes **Reasoning Agents** to analyze financial data and a **Retrieval-Augmented Generation (RAG)** pipeline to cross-reference decisions against internal banking credit policies.

**Role:** GenAI Engineering Lead Capstone  
**Tech Stack:** Python, AWS Bedrock (Claude 3), LangChain, Streamlit, FAISS  

---

## 🏗️ System Architecture

### 1. The Orchestrator (Brain)
* **Model:** Anthropic Claude 3 Sonnet (via AWS Bedrock).
* **Role:** Acts as the central controller. It receives the User's loan application and decides which "Tools" to call.

### 2. The Tools (Capabilities)
* **Tool A: Policy Retriever (RAG)**
    * *Function:* Searches the "Bank Credit Policy" vector database.
    * *Use Case:* "What is the max Loan-to-Value (LTV) ratio for a Tier 2 client?"
* **Tool B: Financial Calculator**
    * *Function:* Python-based logic for DSCR (Debt Service Coverage Ratio) calculation.
    * *Use Case:* "Calculate cash flow adequacy."

### 3. Safety & Governance
* **Guardrails:** Pre-computation checks to prevent bias (Fair Lending compliance).
* **Human-in-the-Loop (HITL):** A mandatory "Manager Review" step for high-risk loans before the final offer letter is generated.

---

## 🚀 Key Features (Interview Talking Points)
* **Sovereign AI:** Runs entirely on private AWS infrastructure (Bedrock).
* **Explainability:** Every decision cites specific clauses from the Policy PDF.
* **Hybrid Evaluation:** Uses "LLM-as-a-Judge" to grade risk memos against gold-standard examples.