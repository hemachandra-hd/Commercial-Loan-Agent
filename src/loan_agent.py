import boto3
import json
#from rag_backend import search_policy
# --- PATH FIX ---
# This allows the script to find 'rag_backend' whether we run it directly OR from app.py
try:
    # Try importing as if we are running from the App (root folder)
    from src.rag_backend import search_policy
except ImportError:
    # If that fails, import as if we are running the script directly (inside src)
    from rag_backend import search_policy
# ----------------



# Initialize Bedrock Client
bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

def ask_claude(question):
    print(f"\n🤖 Agent is thinking about: '{question}'...")
    
    # 1. RETRIEVE context from our Knowledge Base
    # We search for the 3 most relevant chunks of the policy
    print("📚 Consulting the Rule Book (RAG)...")
    results = search_policy(question)
    
    # Combine the retrieved text chunks into one big string
    context_text = "\n\n".join([doc.page_content for doc in results])
    
    # 2. PREPARE the Prompt (The "System Instructions")
    # This is where we give the AI its persona.
    prompt = f"""
    You are a Senior Commercial Credit Officer at ACME Banking. 
    Your goal is to assess loan applications strictly based on the BANK POLICY provided below.
    
    <BANK_POLICY>
    {context_text}
    </BANK_POLICY>
    
    USER QUESTION: {question}
    
    INSTRUCTIONS:
    - If the policy explicitly forbids the loan, say "REJECTED" and quote the specific rule.
    - If the policy allows it but requires specific conditions (like LTV), mention them.
    - If the answer is not in the policy, say "I cannot find a rule regarding this in the policy."
    - Be professional, concise, and direct.
    """

    # 3. CALL Claude (The Model)
    # We use the Messages API format required for Claude 3
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    response = bedrock.invoke_model(
        body=body,
        modelId="anthropic.claude-3-sonnet-20240229-v1:0", # Check if you have Sonnet or Haiku enabled
        accept="application/json",
        contentType="application/json"
    )

    # 4. PARSE the Response
    response_body = json.loads(response.get("body").read())
    answer = response_body["content"][0]["text"]
    
    return answer

# Test Area
# if __name__ == "__main__":
#     print("🚀 STARTING AGENT STRESS TEST...")
#     # Test Case 1: Simple numeric check
#     answer = ask_claude("The borrower has a credit score of 600. Can we approve?")
#     print("\n💬 CLAUDE'S ANSWER:\n" + answer)
    
#     print("-" * 50)
    
#     # Test Case 2: The "Trap" (Industry restriction)
#     answer2 = ask_claude("A new Crypto Exchange wants a loan. Good idea?")
#     print("\n💬 CLAUDE'S ANSWER:\n" + answer2)

# ... (Keep the imports and ask_claude function exactly as they are) ...

# Test Area - Expanded for Robustness
if __name__ == "__main__":
    print("🚀 STARTING AGENT STRESS TEST...")
    
    # Case 1: The Authority Limit Logic (Requires understanding hierarchies)
    # Rule: > $5M requires Executive Committee
    question1 = "I need to approve a $6,000,000 loan for a factory. I am a Senior Credit Officer. Can I sign this alone?"
    print(f"\n❓ Q1: {question1}")
    print(ask_claude(question1))
    
    # Case 2: The LTV Math Check (Requires comparing two numbers)
    # Rule: Equipment LTV limit is 80%
    question2 = "Client wants $90,000 to buy a $100,000 piece of machinery (90% LTV). Can we do it?"
    print(f"\n❓ Q2: {question2}")
    print(ask_claude(question2))

    # Case 3: The Unsecured Cap (Requires checking the specific loan type limit)
    # Rule: Unsecured limit is $100k
    question3 = "A long-time customer needs $150,000 signature loan (unsecured) for working capital."
    print(f"\n❓ Q3: {question3}")
    print(ask_claude(question3))
    
    # Case 4: The Edge Case (Technically allowed, but borderline)
    # Rule: Minimum DSCR is 1.25x
    question4 = "The borrower has a DSCR of 1.30x. Is that sufficient?"
    print(f"\n❓ Q4: {question4}")
    print(ask_claude(question4))


    # Case 5: The Edge Case (Technically allowed, but borderline)
    # Rule: Minimum DSCR is 1.25x
    question4 = "what is the capital of India?"
    print(f"\n❓ Q4: {question4}")
    print(ask_claude(question4))


    # Case 6: The Edge Case (Technically allowed, but borderline)
    # Rule: Minimum DSCR is 1.25x
    question4 = "what is min credit score required for student loan approval ?"
    print(f"\n❓ Q4: {question4}")
    print(ask_claude(question4))