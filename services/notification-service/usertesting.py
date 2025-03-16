import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# AWS SES SMTP credentials
smtp_server = "email-smtp.ap-southeast-2.amazonaws.com"
smtp_port = 456
smtp_username = os.environ.get('AWS_SES_ACCESS_KEY', '')
smtp_password =  os.environ.get('AWS_SES_SECRET_KEY', '') # Your actual secret key

# Email details
sender = "mulanesdevents@gmail.com"
recipient = "diyaj.d.2023@scis.smu.edu.sg"  # Must be verified in sandbox
subject = "Test Email from Python"
body = "<p>This is a test email sent using AWS SES via Python.</p>"

# Create message
message = MIMEMultipart()
message["From"] = sender
message["To"] = recipient
message["Subject"] = subject
message.attach(MIMEText(body, "html"))

# Connect to server
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()  # Enable TLS
    server.ehlo()
    server.login(smtp_username, smtp_password)
    
    # Send email
    server.sendmail(sender, recipient, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    server.quit() if 'server' in locals() else None