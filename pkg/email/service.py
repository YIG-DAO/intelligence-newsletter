import re
import time
import smtplib, ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import time
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def validate_email(email):
    """
    Check if the email is properly formatted.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is properly formatted, False otherwise.
    """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) 

def process_emails(email_tuples):
    """
    Removes duplicates and misformatted emails from a list of email tuples.

    Args:
        email_tuples (list): A list of tuples containing email addresses.

    Returns:
        list: A list of tuples containing processed email addresses.

    """
    # Using a set to automatically remove duplicates
    processed_emails = set()

    for email_tuple in email_tuples:
        # Extract the email from the tuple
        email = email_tuple[0]

        # Check if the email is valid
        if validate_email(email):
            processed_emails.add(email)

    # Convert back to a list of tuples
    return [(email,) for email in processed_emails]

def validate_email(email):
    """
    Check if the email is properly formatted.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is properly formatted, False otherwise.
    """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) 

def process_emails(email_tuples):
    """
    Removes duplicates and misformatted emails from a list of email tuples.

    Args:
        email_tuples (list): A list of tuples containing email addresses.

    Returns:
        list: A list of tuples containing processed email addresses.

    """
    # Using a set to automatically remove duplicates
    processed_emails = set()
    for email_tuple in email_tuples:
        # Extract the email from the tuple
        email = email_tuple[0]
        # Check if the email is valid
        if validate_email(email):
            processed_emails.add(email)
    # Convert back to a list of tuples
    return [(email,) for email in processed_emails]

def send_email_html(sender_email, receiver_email, html, date, smtp_server, port, smtp_user, smtp_password):
    """
    Send an email with HTML content.

    Args:
        sender_email (str): The email address of the sender.
        receiver_email (str): The email address of the receiver.
        html (str): The HTML content of the email.
        date (str): The date of the email.
        smtp_server (str): The SMTP server address.
        port (int): The port number for the SMTP server.
        smtp_user (str): The username for SMTP authentication.
        smtp_password (str): The password for SMTP authentication.
    """
    print(f"> Sending email to {receiver_email}")
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"Yeetum Intelligence - {date}"

    part1 = MIMEText(html, 'html')
    msg.attach(part1)
    # Send email
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo() 
        server.starttls(context=context)
        server.ehlo() 
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        # Close SMTP connection
        server.quit()

def send(processed_emails, cfg, html, today):
    """
    Send emails to the processed email addresses.
    
    Args:
        processed_emails (list): List of processed email addresses.
        cfg (object): Configuration object containing sender email, SMTP server details, etc.
        html (str): The HTML content of the email.
        today (str): The date of the email.
    """
    for processed_email in processed_emails:
        try:
            send_email_html(cfg.sender_email, processed_email[0], html, today, cfg.smtp_server, cfg.port, cfg.smtp_user, cfg.smtp_password)
            time.sleep(5)
        except Exception as e:
            print(f"Error sending email to {processed_email[0]}: {str(e)}")