import requests
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import json
import os

def load_urls(file_path="urls.json"):
    """Load URLs from a JSON file."""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({"urls": []}, f)
        return []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get("urls", [])
    except Exception as e:
        print(f"Error loading URLs: {e}")
        return []

def save_urls(urls, file_path="urls.json"):
    """Save URLs to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump({"urls": urls}, f)
    except Exception as e:
        print(f"Error saving URLs: {e}")

def check_website_status(url):
    """Check if a website is live. Returns (message, is_live)."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"{url} is live at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Status code: {response.status_code}", True
        else:
            return f"{url} is down at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Status code: {response.status_code}", False
    except requests.exceptions.RequestException as e:
        return f"{url} is down at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Error: {str(e)}", False

def send_notification(message, smtp_config):
    """Send email notification for down URLs."""
    try:
        msg = MIMEText(message)
        msg['Subject'] = 'Website Status Alert'
        msg['From'] = smtp_config['sender']
        msg['To'] = smtp_config['receiver']
        with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['sender'], smtp_config['password'])
            server.sendmail(smtp_config['sender'], smtp_config['receiver'], msg.as_string())
        return f"Notification sent: {message}"
    except Exception as e:
        return f"Failed to send notification: {str(e)}"

def log_result(message, log_file="website_status.log"):
    """Log results to a file."""
    try:
        with open(log_file, 'a') as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f"Error logging result: {e}")

def monitor_websites(smtp_config, url_file="urls.json", log_file="website_status.log"):
    """Monitor all URLs every 10 minutes."""
    while True:
        urls = load_urls(url_file)
        if not urls:
            print("No URLs to monitor. Waiting 10 minutes...")
            log_result("No URLs to monitor at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
        for url in urls:
            result, is_live = check_website_status(url)
            log_result(result, log_file)
            print(result)
            if not is_live:
                notification_result = send_notification(result, smtp_config)
                log_result(notification_result, log_file)
                print(notification_result)
        time.sleep(600)  # Wait 10 minutes

if __name__ == "__main__":
    smtp_config = {
        'server': 'smtp.gmail.com',
        'port': 587,
        'sender': 'your_email@gmail.com',  # Replace with your email
        'receiver': 'your_email@gmail.com',  # Replace with recipient email
        'password': 'your-app-specific-password'  # Replace with Gmail app-specific password
    }
    # Initialize urls.json if it doesn't exist
    if not os.path.exists("urls.json"):
        save_urls([], "urls.json")
    print("Starting website monitoring...")
    monitor_websites(smtp_config)