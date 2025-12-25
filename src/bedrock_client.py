print("🚀 Script is starting...")  # <--- Add this line at the very top

import boto3
import json
import sys

def test_bedrock():
    print("⏳ Connecting to AWS Bedrock...")
    
    try:
        # Setup the Client
        bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
        
        # Define the Model and Prompt
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        prompt = "Hello Claude. Are you ready?"
        
        # Format payload
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        # Invoke
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(payload)
        )
        
        # Parse
        result = json.loads(response.get("body").read())
        answer = result['content'][0]['text']
        
        print("\n✅ SUCCESS! Connection Established.")
        print(f"🤖 Claude says: {answer}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

# --- MAKE SURE THIS PART IS CORRECT ---
if __name__ == "__main__":
    test_bedrock()