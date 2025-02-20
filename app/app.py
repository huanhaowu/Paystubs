import os
import pandas as pd
from flask import Flask, request, jsonify, Response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from lib.send_email import send_payroll_email
from typing import Optional, Dict

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

# User credentials stored in environment variables
users: Dict[Optional[str], str]  = {
    os.getenv('AUTH_USERNAME'): generate_password_hash(os.getenv('AUTH_PASSWORD'))
}

@auth.verify_password
def verify_password(username: str, password: str) -> Optional[str]:
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

@app.route('/')
def home() -> str:
    return "Welcome to the paystubs - assessment"

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file() -> Response:
    required_columns = [
        "full_name", "email", "position", "health_discount_amount",
        "social_discount_amount", "taxes_discount_amount", "other_discount_amount",
        "gross_salary", "gross_payment", "net_payment", "period"
    ]

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    country = request.form.get('country', 'do').lower()
    company = request.form.get('company', 'ATDEv').lower()

    if country not in ['do', 'usa']:
        return jsonify({"error": "Country not defined. Only registered Dominican Republic and United States"}), 400

    if file and file.filename.endswith('.csv'):
        # Read the CSV file
        df: pd.DataFrame = pd.read_csv(file)

        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({"error": f"Missing columns: {', '.join(missing_columns)}"}), 400

        # Validate email column
        for index, row in df.iterrows():
            email = row['email']
            try:
                validate_email(email)
            except EmailNotValidError as e:
                return jsonify({"error": f"Invalid email '{email}' for employee {row['full_name']} - {str(e)}"}), 400

        # Validate period column
        try:
            df['period'] = pd.to_datetime(df['period'], format='%Y-%m-%d')
        except Exception as e:
            return jsonify({"error": f"Invalid date format in period column: {e}"}), 400

        # Send email with payroll data
        email_results = send_payroll_email(df, country, company)

        # Return JSON with successfully sent emails and timestamps
        return jsonify({"email_results": email_results})

    return jsonify({"error": "Invalid file format, only .csv files are allowed"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
