import re
import time
import smtplib, ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

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
    msg['Subject'] = f"Report - {date}"

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

def render_html(template, data):
    """
    Render an HTML template with the given data.

    Args:
        template (str): The path to the HTML template file.
        data (dict): The data to render in the template.

    Returns:
        str: The rendered HTML content.
    """
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template)
    return template.render(data)

def render_sentiment_html(report_data):
    """
    Render the sentiment data in an HTML template.

    Args:
        sentiment (list): A list of sentiment data.

    Returns:
        str: The rendered HTML content.
    """
    # Top 3 sentiment
    sentiment = []
    for sent in report_data['sentiment']:
        symbol = sent['symbol']
        score = sent['sent_score']
        last_score = sent['last_sentiment']
        sent_format = f'<table><tr><td>Symbol:</td><td>{symbol}</td></tr><tr><td>Sentiment:</td><td>{score}</td></tr><tr><td>Previous:</td><td>{last_score}</td></tr></table>'
        sentiment.append(sent_format)
    return sentiment

def render_insider_html(report_data):
    """
    Render the insider data in an HTML template.

    Args:
        insider (list): A list of insider data.

    Returns:
        str: The rendered HTML content.
    """
    insider = []
    insider_link = []
    for ins in report_data['insider_trades']:
        symbol = ins['symbol']
        transaction = ins['transactionType']
        amount = ins['securitiesTransacted']
        link = ins['link']
        insider_format = f'<table><tr><td>Symbol:</td><td>{symbol}</td></tr><tr><td>Transaction:</td><td>{transaction}</td></tr><tr><td>Amount:</td><td>{amount}</td></tr></table>'
        insider.append(insider_format)
        insider_link.append(link)
    return insider, insider_link

def render_gov_contracts_html(report_data):
    """
    Renders the government contracts data as HTML.

    Args:
        report_data (dict): A dictionary containing the report data.

    Returns:
        list: A list of HTML-formatted contracts.

    """
    contracts = []
    for cont in report_data['gov_contracts']:
        agency = cont['Agency']
        amount = cont['Amount']
        ticker = cont['Ticker']
        cont_format =  f'<table><tr><td>Agency:</td><td>{agency}</td></tr><tr><td>Amount:</td><td>{amount}</td></tr><tr><td>Ticker:</td><td>{ticker}</td></tr></table>'
        contracts.append(cont_format)
    return contracts

def render_cve_html(report_data):
    """
    Renders the CVE data as HTML.

    Args:
        report_data (dict): A dictionary containing the report data.

    Returns:
        list: A list of HTML-formatted CVEs.

    """
    cve = []
    cve_link = []
    for cv in report_data['cve']:
        id = cv['id']
        link = cv['link']
        cve_format = id
        cve.append(cve_format)
        cve_link.append(link)
    return cve, cve_link

def generate_report_html(cfg, today, exec_synopsis, sentiment, insider, insider_link, contract, cve, cve_link, ysi1_t, ysi1_l, ysi2_t, ysi2_l, ysi3_t, ysi3_l, ysi4_t, ysi4_l, ysi5_t, ysi5_l):
    """
    Generate the HTML content for the report.

    Args:
        cfg (object): Configuration object containing logo path.
        today (str): The date of the report.
        exec_synopsis (str): The execution synopsis.
        sentiment (list): A list of sentiment data.
        insider (list): A list of insider data.
        insider_link (list): A list of insider links.
        contract (list): A list of government contracts data.
        cve (list): A list of CVE data.
        cve_link (list): A list of CVE links.
        ysi1_t (str): The title for YSI1.
        ysi1_l (str): The link for YSI1.
        ysi2_t (str): The title for YSI2.
        ysi2_l (str): The link for YSI2.
        ysi3_t (str): The title for YSI3.
        ysi3_l (str): The link for YSI3.
        ysi4_t (str): The title for YSI4.
        ysi4_l (str): The link for YSI4.
        ysi5_t (str): The title for YSI5.
        ysi5_l (str): The link for YSI5.

    Returns:
        str: The rendered HTML content.
    """
    env = Environment(loader=FileSystemLoader('html'))
    template = env.get_template('report.html')
    html = template.render(logo=cfg.logo, DATETIME=today, YEETGPT_EXEC_SYNOPSIS=exec_synopsis,
                            sent1=sentiment[0], sent2=sentiment[1], sent3=sentiment[2],
                            insider1=insider[0], insider2=insider[1], insider3=insider[2],
                            insider_link1=insider_link[0], insider_link2=insider_link[1], insider_link3=insider_link[2],
                            gov_con1=contract[0], gov_con2=contract[1], gov_con3=contract[2],
                            cve1=cve[0], cve2=cve[1], cve3=cve[2],
                            cve_link1=cve_link[0], cve_link2=cve_link[1], cve_link3=cve_link[2],
                            ysi1_t=ysi1_t, ysi1_l=ysi1_l,
                            ysi2_t=ysi2_t, ysi2_l=ysi2_l,
                            ysi3_t=ysi3_t, ysi3_l=ysi3_l,
                            ysi4_t=ysi4_t, ysi4_l=ysi4_l,
                            ysi5_t=ysi5_t, ysi5_l=ysi5_l)
    return html