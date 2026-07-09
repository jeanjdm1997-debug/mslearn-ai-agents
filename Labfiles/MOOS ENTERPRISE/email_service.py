import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_invoice_request(
        client_name,
        company_name,
        email,
        phone,
        service_required,
        additional_notes
):
    receiver = os.getenv("company_email") or ""
    sender = os.getenv("smtp_username") or ""
    password = os.getenv("smtp_password") or ""
    subject = f"New Invoice Request - {company_name}"
    body = f"""
A new quotation request has been submitted.

Client_Name: {client_name}

Company:
{company_name}

Email:
{email}

Phone:
{phone}

Requested_Service:
{service_required}

Additional_Notes:
{additional_notes}
"""
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(
        os.getenv("SMTP_Server") or "localhost",
        int(os.getenv("SMTP_Port") or "587")
    ) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(message)

        return "Invoice Request Sent Successfully. A Consultant Will Respond To Your Request Within 24-Hours."