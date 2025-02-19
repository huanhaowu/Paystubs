from io import BytesIO
from reportlab.pdfgen import canvas
import os
from datetime import datetime
from typing import Optional

def generate_pdf(
    full_name: str,
    email: str,
    position: str,
    health_discount_amount: float,
    social_discount_amount: float,
    taxes_discount_amount: float,
    other_discount_amount: float,
    gross_salary: float,
    gross_payment: float,
    net_payment: float,
    period: datetime,
    company_name: str,
    country: str
) -> Optional[bytes]:
    buffer: BytesIO = BytesIO()
    pdf = canvas.Canvas(buffer)

    # Titles and labels based on country
    if country == 'do':
        title: str = f"{company_name} - Comprobante de Pago"
        period_label: str = "Periodo"
        name_label: str = "Nombre"
        email_label: str = "Email"
        position_label: str = "Posición"
        gross_salary_label: str = "Salario Bruto"
        gross_payment_label: str = "Pago Bruto"
        discounts_label: str = "Descuentos"
        health_insurance_label: str = "SFS"
        social_security_label: str = "AFP"
        taxes_label: str = "ISR"
        others_label: str = "Otros"
        total_discounts_label: str = "Total Descuentos"
        net_payment_label: str = "Pago Neto"
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
        base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get 'app' directory
        logo_directory: str = os.path.join(base_dir, "static")  # Adjusted to match your structure
        logo_filename: str = f"{company_name}.png"  # Convert company name to filename
        logo_path: str = os.path.join(logo_directory, logo_filename)

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

        total_discounts: float = social_discount_amount + health_discount_amount + taxes_discount_amount + other_discount_amount
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