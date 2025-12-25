import csv
import os
from datetime import datetime

LOG_FILE = "feedback_log.csv"

def log_feedback(inputs, ai_response, rating, correction=""):
    """
    Saves the interaction data to a CSV file for future training.
    """
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write header if new file
        if not file_exists:
            writer.writerow(["Timestamp", "Applicant", "Loan_Amount", "Credit_Score", "Details", "AI_Response", "Rating", "Human_Correction"])
            
        # Write the data row
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            inputs.get("applicant"),
            inputs.get("amount"),
            inputs.get("score"),
            inputs.get("details"),
            ai_response,
            rating,
            correction
        ])
    
    return True