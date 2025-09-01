import os 
import requests
from dotenv import load_dotenv

load_dotenv()

def send_simple_message(to, subject, text):
    mail_domain = os.getenv('MAIL_DOMAIN')
    return requests.post(
        f"https://api.mailgun.net/v3/{mail_domain}/messages",
        auth=("api", os.getenv('MAIL_API_KEY')),
        data={"from": f"Bryan Thomas <postmaster@{mail_domain}>",
              "to": [to],
              "subject": subject,
              "text": text})

def send_user_registration_email(username, email):
    subject = "Welcome to our Store API"
    text = f"Thank you for registering, {username}!"
    return send_simple_message(to=email, subject=subject, text=text)