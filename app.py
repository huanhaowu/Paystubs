import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from io import BytesIO

import pandas as pd
import pytz
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.pdfgen import canvas
from email_validator import validate_email, EmailNotValidError

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
    company = request.form.get('company', 'ATDEv').lower()

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
        for email in df['email']:
            try:
                validate_email(email)
            except EmailNotValidError as e:
                return jsonify({"error": f"Invalid email '{email}' - {str(e)}"}), 400

        # Validate period column
        try:
            df['period'] = pd.to_datetime(df['period'], format='%Y-%m-%d')
        except Exception as e:
            return jsonify({"error": f"Invalid date format in period column: {e}"}), 400

        # Send email with payroll data
        email_results = send_payroll_email(df, country, company)

        # Return the CSV content as JSON
        # json_data = df.to_dict(orient='records')
        # return jsonify({"csv_data": json_data})

        # Return JSON with successfully sent emails and timestamps
        return jsonify({"email_results": email_results})

    return jsonify({"error": "Invalid file format, only .csv files are allowed"}), 400


def generate_pdf(full_name, email, position, health_discount_amount, social_discount_amount,
                 taxes_discount_amount, other_discount_amount, gross_salary, gross_payment,
                 net_payment, period, company_name, country):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    # Titles and labels based on country
    if country == 'do':
        title = f"{company_name} - Comprobante de Pago"
        period_label = "Periodo"
        name_label = "Nombre"
        email_label = "Email"
        position_label = "Posición"
        gross_salary_label = "Salario Bruto"
        gross_payment_label = "Pago Bruto"
        discounts_label = "Descuentos"
        health_insurance_label = "SFS"
        social_security_label = "AFP"
        taxes_label = "ISR"
        others_label = "Otros"
        total_discounts_label = "Total Descuentos"
        net_payment_label = "Pago Neto"
    else:
        title = f"{company_name} - Paystub Payment"
        period_label = "Period"
        name_label = "Full Name"
        email_label = "Email"
        position_label = "Position"
        gross_salary_label = "Gross Salary"
        gross_payment_label = "Gross Payment"
        discounts_label = "Discounts"
        health_insurance_label = "Health Insurance"
        social_security_label = "Social Security"
        taxes_label = "Taxes"
        others_label = "Others"
        total_discounts_label = "Total Discounts"
        net_payment_label = "Net Payment"

    try:
        # Title
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(200, 800, title)

        # Dynamically set the logo path based on company name
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        logo_directory = os.path.join(BASE_DIR, "assets")

        logo_filename = f"{company_name.lower().replace(' ', '_')}.png"  # Convert company name to filename
        logo_path = os.path.join(logo_directory, logo_filename)

        # Add company logo if it exists
        if os.path.exists(logo_path):
            pdf.drawImage(logo_path, 200, 750, width=150, height=50, preserveAspectRatio=True, mask='auto')
        else:
            print(f"Warning: Logo for '{company_name}' not found at {logo_path}")

        # General Information
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 700, f"{period_label}: {period}")
        pdf.drawString(100, 680, f"{name_label}: {full_name}")
        pdf.drawString(100, 660, f"{email_label}: {email}")
        pdf.drawString(100, 640, f"{position_label}: {position}")

        # Salary Details
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 610, f"{gross_salary_label}:")
        pdf.drawString(250, 610, f"{gross_salary}")

        pdf.drawString(100, 590, f"{gross_payment_label}:")
        pdf.drawString(250, 590, f"{gross_payment}")

        # Discounts
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 560, f"{discounts_label}:")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(120, 540, f"{health_insurance_label}: {social_discount_amount}")
        pdf.drawString(120, 520, f"{social_security_label}: {health_discount_amount}")
        pdf.drawString(120, 500, f"{taxes_label}: {taxes_discount_amount}")
        pdf.drawString(120, 480, f"{others_label}: {other_discount_amount}")

        total_discounts = social_discount_amount + health_discount_amount + taxes_discount_amount + other_discount_amount
        pdf.drawString(120, 460, f"{total_discounts_label}: {total_discounts}")

        # Net Payment
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 430, f"{net_payment_label}:")
        pdf.drawString(250, 430, f"{net_payment}")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        print(f"Failed to generate PDF: {e}")
        return None

def send_payroll_email(df, country, company):
    sender_email = 'huanhaowu28@gmail.com'
    sender_password = 'ewdjflzbzhkeruzl'
    smtp_server = 'smtp.gmail.com'
    smtp_port = int(os.getenv('SMTP_PORT'))

    email_results = []

    # Dominican Republic timezone
    dr_tz = pytz.timezone('America/Santo_Domingo')

    for index, row in df.iterrows():
        recipient_email = row['email']
        # recipient_email = 'huanhaowu28@gmail.com'
        company_name = company  # Replace with your company name

        # Generate PDF
        pdf_content = generate_pdf(
            row['full_name'], row['email'], row['position'], row['health_discount_amount'],
            row['social_discount_amount'], row['taxes_discount_amount'], row['other_discount_amount'],
            row['gross_salary'], row['gross_payment'], row['net_payment'], row['period'], company_name, country
        )

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

        # Attach PDF
        pdf_attachment = MIMEApplication(pdf_content, _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"{row['full_name']}_paystub.pdf")
        msg.attach(pdf_attachment)

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