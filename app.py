import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import pytz
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

# User credentials stored in environment variables
users = {
    os.getenv('AUTH_USERNAME'): generate_password_hash(os.getenv('AUTH_PASSWORD'))
}


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None


@app.route('/')
def home():
    return "Welcome to the paystubs - assessment"


@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
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

    if country not in ['do', 'usa']:
        return jsonify({"error": "Country not defined. Only registered Dominican Republic and United States"}), 400

    if file and file.filename.endswith('.csv'):
        # Read the CSV file
        df = pd.read_csv(file)

        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({"error": f"Missing columns: {', '.join(missing_columns)}"}), 400

        # Validate email column
        # for email in df['email']:
        #     try:
        #         validate_email(email)
        #     except EmailNotValidError as e:
        #         return jsonify({"error": str(e)}), 400

        # Validate period column
        try:
            df['period'] = pd.to_datetime(df['period'], format='%Y-%m-%d')
        except Exception as e:
            return jsonify({"error": f"Invalid date format in period column: {e}"}), 400

        # Send email with payroll data
        email_results = send_payroll_email(df, country)

        # Return the CSV content as JSON
        # json_data = df.to_dict(orient='records')
        # return jsonify({"csv_data": json_data})

        # Return JSON with successfully sent emails and timestamps
        return jsonify({"email_results": email_results})

    return jsonify({"error": "Invalid file format, only .csv files are allowed"}), 400


def send_payroll_email(df, country):
    sender_email = 'huanhaowu28@gmail.com'
    sender_password = 'ewdjflzbzhkeruzl'
    smtp_server = 'smtp.gmail.com'
    smtp_port = int(os.getenv('SMTP_PORT'))

    email_results = []

    # Dominican Republic timezone
    dr_tz = pytz.timezone('America/Santo_Domingo')

    for index, row in df.iterrows():
        recipient_email = 'huanhaowu28@gmail.com'

        if country == 'do':
            subject = "Comprobante de Pago"
            body = f"""
                    Comprobante de Pago para {row['full_name']}:
                    Email: {row['email']}
                    Posición: {row['position']}
                    Periodo: {row['period'].strftime('%Y-%m-%d')}

                    SFS: {row['health_discount_amount']}
                    AFP: {row['social_discount_amount']}
                    ISR: {row['taxes_discount_amount']}
                    Otros: {row['other_discount_amount']}
                    Salario Bruto: {row['gross_salary']}
                    Pago Bruto: {row['gross_payment']}
                    Pago Neto: {row['net_payment']}
                    """
        else:
            subject = "Paystub Payment"
            body = f"""
                    Paystub Payment for {row['full_name']}:
                    Email: {row['email']}
                    Position: {row['position']}
                    Period: {row['period'].strftime('%Y-%m-%d')}

                    Health Insurance: {row['health_discount_amount']}
                    Social Security: {row['social_discount_amount']}
                    Taxes: {row['taxes_discount_amount']}
                    Others: {row['other_discount_amount']}
                    Gross Salary: {row['gross_salary']}
                    Gross Payment: {row['gross_payment']}
                    Net Payment: {row['net_payment']}
                    """

        # Create email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            email_results.append({
                "email": recipient_email,
                "status": "success",
                "timestamp": datetime.now(dr_tz).strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"Email sent successfully to {recipient_email}")
        except Exception as e:
            email_results.append({
                "email": recipient_email,
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(dr_tz).strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"Failed to send email to {recipient_email}: {e}")

    return email_results


if __name__ == '__main__':
    app.run(debug=True)
