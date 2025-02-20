import os
from io import BytesIO
from typing import Optional
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER

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
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    date_str = period.strftime("%Y-%m-%d")

    # Títulos y etiquetas basados en el país
    if country.lower() == 'do':
        title: str = f"Comprobante de pago"
        subtitle: str = f"({date_str})"
        name_label: str = "Nombre"
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
        title = f"Paystub Payment"
        subtitle = f"({date_str})"
        name_label = "Full Name"
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
        # ---------- LOGO ----------
        base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_directory: str = os.path.join(base_dir, "static")
        logo_filename: str = f"{company_name}.png"
        logo_path: str = os.path.join(logo_directory, logo_filename)

        if not os.path.exists(logo_path):
            logo_path = os.path.join(logo_directory, "default.png")

        if os.path.exists(logo_path):
            pdf.drawImage(
                logo_path,
                260, 700,
                width=100,
                height=50,
                preserveAspectRatio=True,
                mask='auto'
            )

        # ---------- ENCABEZADO / TÍTULOS ----------
        pdf.setFont("Helvetica-Bold", 20)
        if country.lower() == 'do':
            pdf.drawString(190, 680, title)
        else:
            pdf.drawString(230, 680, title)

        pdf.setFont("Helvetica", 14)
        pdf.drawString(260, 660, subtitle)

        # ---------- DATOS PERSONALES ----------
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 580, f"{name_label}:")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(150, 580, full_name)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 560, f"{position_label}:")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(150, 560, position)

        # ---------- DETALLES SALARIALES ----------
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 510, f"{gross_salary_label}:")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(190, 510, f"{gross_salary:.2f}")

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 490, f"{gross_payment_label}:")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(190, 490, f"{gross_payment:.2f}")

        # ---------- DESCUENTOS / DISCOUNTS ----------
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 460, f"{discounts_label}:")

        pdf.setFont("Helvetica", 16)
        pdf.drawString(70, 440, f"{health_insurance_label}:   {health_discount_amount:.2f}")
        pdf.drawString(70, 420, f"{social_security_label}:   {social_discount_amount:.2f}")
        pdf.drawString(70, 400, f"{taxes_label}:   {taxes_discount_amount:.2f}")
        pdf.drawString(70, 380, f"{others_label}:   {other_discount_amount:.2f}")

        total_discounts = (
                health_discount_amount
                + social_discount_amount
                + taxes_discount_amount
                + other_discount_amount
        )
        pdf.drawString(70, 360, f"{total_discounts_label}:   {total_discounts:.2f}")

        # ---------- PAGO NETO / NET PAYMENT ----------
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 330, f"{net_payment_label}:")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(180, 330, f"{net_payment:.2f}")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        print(f"Failed to generate PDF: {e}")
        return None
