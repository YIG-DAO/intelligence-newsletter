import os
import json
import psycopg2
import time
import openai

from jinja2 import Environment, FileSystemLoader
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler
# Import DB Connectivity
from db.index import fetch_email_list

# Import custom embedded packages
from pkg.osint import service as osint
from pkg.llm import service as ai
from pkg.email import service as email_service
from pkg.shared import config as cfg

scheduler = BlockingScheduler()
openai.api_key = cfg.openai_api_key

def main():
    today = str(date.today())
    print("###################################")
    print(f"# Email Intel Report Job {today}#")
    print("###################################")
    try:
        # Extract Data
        report_data = osint.extract_data(cfg.ysi_feed, cfg.sent_url, cfg.contract_url, cfg.insider_url, cfg.cve_url)
        processed_report_data = json.dumps(report_data)

        # Top 3 sentiment
        sentiment = email_service.render_sentiment_html(report_data)        
        # Top 3 insider
        insider, insider_link = email_service.render_insider_html(report_data)
        # Top 3 gov contract
        contract = email_service.render_gov_contracts_html(report_data)
        # Top 3 CVE
        cve, cve_link = email_service.render_cve_html(report_data)

        processed_rss = report_data['rss']
    
        exec_synopsis = ai.GPT4(processed_report_data)
    
        email_report = email_service.generate_report_html(cfg, today, exec_synopsis, sentiment, insider, insider_link, contract, cve, cve_link, processed_rss['ysi_0'][0], processed_rss['ysi_0'][1], processed_rss['ysi_1'][0], processed_rss['ysi_1'][1], processed_rss['ysi_2'][0], processed_rss['ysi_2'][1], processed_rss['ysi_3'][0], processed_rss['ysi_3'][1], processed_rss['ysi_4'][0], processed_rss['ysi_4'][1])
        receiver_emails = fetch_email_list()

        # Process Email List then Send 
        processed_emails = email_service.process_emails(receiver_emails)
        email_service.send(processed_emails, cfg, email_report, today)

    except Exception as e:
        # Handle exceptions here
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'cron', day_of_week='mon', hour=13)
    scheduler.add_job(main, 'cron', day_of_week='fri', hour=13)
    scheduler.start()
