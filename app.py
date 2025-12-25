import streamlit as st
import src.loan_agent as agent
from src.guardrails import PIIGuard # <-- Add this new import
from src.feedback import log_feedback  # <-- Add this

# 1. Page Config
st.set_page_config(page_title="Commercial Loan Risk Agent", page_icon="🏦", layout="centered")

# --- SESSION STATE INITIALIZATION ---
if 'output' not in st.session_state:
    st.session_state['output'] = ""
if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

# Function to reset the app
def reset_app():
    st.session_state['output'] = ""
    st.session_state['analyzed'] = False

# --- VALIDATION ENGINE (The New Logic) ---
def validate_inputs(name, amount, score, details):
    errors = []
    
    # Rule 1: Name Check
    if not name or len(name.strip()) < 2:
        errors.append("❌ Applicant Name is required.")
        
    # Rule 2: Loan Amount logic
    if amount <= 0:
        errors.append("❌ Loan amount must be greater than $0.")
    elif amount < 5000:
        errors.append("⚠️ Minimum loan amount is $5,000 for commercial processing.")
        
    # Rule 3: Credit Score Reality Check
    # (Streamlit number_input handles text, but we enforce the logical range here)
    if score < 300 or score > 850:
        errors.append("❌ FICO Score must be between 300 and 850.")
        
    # Rule 4: Details quality check
    if len(details.strip()) < 10:
        errors.append("❌ Please provide more detail in the Loan Purpose section.")
        
    return errors

# ---------------------------------------------------

st.title("🏦 ACME Commercial Banking")
st.header("AI Risk Assessment Agent")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4149/4149663.png", width=100)
    st.success("✅ Connected to Bedrock")
    st.success("✅ Knowledge Base Loaded")  # <-- ADDED BACK
    st.info("Model: Claude 3 Sonnet")
    if st.button("🔄 Reset / Clear", on_click=reset_app):
        st.rerun()

# --- MAIN FORM (The Upgrade) ---
# We use st.form to batch inputs and prevent constant reloading
with st.form("loan_application_form"):
    st.subheader("📝 New Loan Application")
    
    col1, col2 = st.columns(2)
    with col1:
        applicant_name = st.text_input("Applicant / Company Name")
        # Step=1000 makes it easier to type large numbers
        loan_amount = st.number_input("Loan Amount Requested ($)", min_value=0, step=1000, value=100000)

    with col2:
        # We enforce numeric input strictly with Streamlit's widget
        credit_score = st.number_input("FICO SBSS Score", min_value=0, max_value=1000, value=700)
        business_type = st.selectbox("Industry Type", 
            ["Manufacturing", "Retail", "Real Estate", "Crypto/Mining", "Casino/Gambling", "Technology", "Other"]
        )

    st.write("### Loan Purpose & Details")
    loan_purpose = st.text_area(
        "Describe the use of funds and collateral:", 
        height=150,
        placeholder="Example: Client wants to purchase a new warehouse..."
    )
    
    # The Submit Button
    submitted = st.form_submit_button("🚀 Analyze Risk")

# --- PROCESS LOGIC ---
if submitted:
    # 1. Run Input Validation (The "Bouncer")
    validation_errors = validate_inputs(applicant_name, loan_amount, credit_score, loan_purpose)
    
    if validation_errors:
        for error in validation_errors:
            st.error(error)
    else:
        # 2. Run PII Guardrails (The "Safety Shield") - NEW STEP
        guard = PIIGuard()
        safe_details, detected_pii = guard.scrub(loan_purpose)
        
        # If PII was found, warn the user but proceed with the REDACTED text
        if detected_pii:
            st.warning(f"⚠️ Security Alert: We detected and redacted the following PII from your request: {', '.join(detected_pii)}")
            # Debug: Show what the AI will actually see
            with st.expander("See Redacted Data (What the AI sees)"):
            #with st.expander("View Redacted Request"):
                st.code(safe_details)
        
        # 3. Call AI with Safe Data
        with st.spinner("🤖 Consulting the Credit Policy Rules..."):
            query = f"""
            New Loan Application Review:
            - Company: {applicant_name}
            - Industry: {business_type}
            - Loan Amount: ${loan_amount}
            - Credit Score: {credit_score}
            - Details: {safe_details}  <-- We send the scrubbed version!
            
            INSTRUCTIONS:
            1. Check Section 1 (Industries): Is the industry prohibited?
            2. Check Section 2 (Financials): Does the 'Details' imply the business is < 2 years old? (e.g. "Startup", "New business", "Opening"). If yes, REJECT.
            3. Check Section 3 & 4 (Limits/Collateral).
            Based on the Credit Policy, should this be approved?
            """
            
            # Get the decision
            response = agent.ask_claude(query)
            
            # 4. Run Output Guardrails (Check what the AI said) - NEW STEP
            is_safe, safety_msg = guard.validate_content_policy(response)
            
            if not is_safe:
                st.error(f"⛔ System Blocked the AI Response: {safety_msg}")
                st.session_state['output'] = "Response Blocked by Safety Policy."
            else:
                st.session_state['output'] = response
                
            st.session_state['analyzed'] = True

# Display Result
# --- DISPLAY RESULT & FEEDBACK LOOP ---
if st.session_state['analyzed']:
    st.markdown("### 📋 Risk Assessment Decision")
    decision = st.session_state['output']
    
    # Color-coded result
    if "REJECTED" in decision:
        st.error(decision)
    elif "Executive Risk Committee" in decision:
        st.warning(decision)
    else:
        st.success(decision)
        
    st.markdown("---")
    st.write("### 🧠 Human-in-the-Loop Feedback")
    st.info("Help improve the model! Was this decision accurate?")
    
    col_up, col_down = st.columns(2)
    
    # Case 1: Thumbs Up
    with col_up:
        if st.button("👍 Correct"):
            inputs = {
                "applicant": applicant_name,
                "amount": loan_amount,
                "score": credit_score,
                "details": loan_purpose
            }
            log_feedback(inputs, decision, "Positive")
            st.toast("Feedback saved! Helping the model learn...", icon="✅")

    # Case 2: Thumbs Down
    with col_down:
        if st.button("👎 Incorrect"):
            st.session_state['show_correction'] = True

    # Show Correction Box if "Incorrect" was clicked
    if st.session_state.get('show_correction'):
        with st.form("correction_form"):
            human_correction = st.text_area("What should the correct decision have been?", 
                                          placeholder="Example: It should have been approved because...")
            submit_correction = st.form_submit_button("Submit Correction")
            
            if submit_correction:
                inputs = {
                    "applicant": applicant_name,
                    "amount": loan_amount,
                    "score": credit_score,
                    "details": loan_purpose
                }
                log_feedback(inputs, decision, "Negative", human_correction)
                st.success("✅ Correction logged. This will be used for future fine-tuning.")
                st.session_state['show_correction'] = False # Hide box after submit