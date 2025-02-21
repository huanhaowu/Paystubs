import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pytz
import pandas as pd
from typing import List, Dict, Any, Optional
from lib.generate_pdf import generate_pdf


def send_payroll_email(df: pd.DataFrame, country: str, company: str) -> List[Dict[str, Any]]:
    sender_email: str = 'huanhaowu28@gmail.com'
    sender_password: str = 'ewdjflzbzhkeruzl'
    smtp_server: str = 'smtp.gmail.com'
    smtp_port: int = 587

    email_results: List[Dict[str, Any]] = []

    # Dominican Republic timezone
    dr_tz = pytz.timezone('America/Santo_Domingo')

    for index, row in df.iterrows():
        recipient_email: str = row['email']
        company_name: str = company if company else "fakecompany"

        # Generate PDF
        pdf_content: Optional[bytes] = generate_pdf(
            row['full_name'],
            row['email'],
            row['position'],
            row['health_discount_amount'],
            row['social_discount_amount'],
            row['taxes_discount_amount'],
            row['other_discount_amount'],
            row['gross_salary'],
            row['gross_payment'],
            row['net_payment'],
            row['period'],
            company_name,
            country
        )

        if pdf_content is None:
            email_results.append({
                "email": recipient_email,
                "status": "failure",
                "error": "Failed to generate PDF",
                "timestamp": datetime.now(dr_tz).strftime('%Y-%m-%d %H:%M:%S')
            })
            continue

        if country == 'do':
            subject: str = "Comprobante de Pago"
            body: str = f"""
Estimado/a {row['full_name']},
                
Este correo es enviado de parte de {company_name}.
Adjunto encontrará su comprobante de pago correspondiente al período {row['period'].strftime("%Y-%m-%d")}.
                
Saludos cordiales,
{company_name}
            """
        else:
            subject: str = "Paystub Payment"
            body: str = f"""
Dear {row['full_name']},
    
This email is from {company_name}.
Attached is your paystub for the period {row['period'].strftime("%Y-%m-%d")}.
    
Best regards,
{company_name}
            """

        # Create email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach PDF
        pdf_attachment = MIMEApplication(pdf_content, _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"{row['full_name']}_paystub.pdf")
        msg.attach(pdf_attachment)
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
        except Exception as e:
            email_results.append({
                "email": recipient_email,
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(dr_tz).strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"Failed to send email to {recipient_email}: {e}")

    return email_results