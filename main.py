import os
import openai
import json
import psycopg2
import time

from jinja2 import Environment, FileSystemLoader
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler
# Import custom embedded packages
from pkg.osint import service as osint
from pkg.llm import service as ai
from pkg.email import service as email_service
from pkg.shared import config as cfg

# extracting emails to send
conn = psycopg2.connect(
    host=cfg.db_host,   
    port=cfg.db_port,
    database=cfg.db_name,
    user=cfg.db_user,
    password=cfg.db_pw
)
scheduler = BlockingScheduler()

def main():
    print("###################################")
    print("# Starting Email Intel Report Job #")
    print("###################################")
    try:
        processed_rss = osint.rss_process(cfg.ysi_feed)
        processed_sentiment = osint.sent_process(cfg.sent_url)
        processed_gov_contracts = osint.gov_contracts_process(cfg.contract_url)
        processed_insider_trades = osint.insider_trades_process(cfg.insider_url)
        processed_cve = osint.cve_process(cfg.cve_url)
        today = str(date.today())
        report_data = {
            "date": today,
            "gov_contracts": processed_gov_contracts,
            "insider_trades": processed_insider_trades,
            "cve": processed_cve,
            "sentiment": processed_sentiment,
            "rss": processed_rss
        }

        processed_report_data = json.dumps(report_data)

        # Top 3 sentiment
        sentiment = []
        for sent in report_data['sentiment']:
            symbol = sent['symbol']
            score = sent['sent_score']
            last_score = sent['last_sentiment']
            sent_format = f'<table><tr><td>Symbol:</td><td>{symbol}</td></tr><tr><td>Sentiment:</td><td>{score}</td></tr><tr><td>Previous:</td><td>{last_score}</td></tr></table>'
            sentiment.append(sent_format)


        # Top 3 insider
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


        # Top 3 contract
        contract = []
        for cont in report_data['gov_contracts']:
            agency = cont['Agency']
            amount = cont['Amount']
            ticker = cont['Ticker']
            cont_format =  f'<table><tr><td>Agency:</td><td>{agency}</td></tr><tr><td>Amount:</td><td>{amount}</td></tr><tr><td>Ticker:</td><td>{ticker}</td></tr></table>'
            contract.append(cont_format)

        # Top 3 CVE
        cve = []
        cve_link = []
        for cv in report_data['cve']:
            id = cv['id']
            link = cv['link']
            cve_format = id
            cve.append(cve_format)
            cve_link.append(link)

        # ysi 1st article
        ysi1_t = processed_rss['ysi_0'][0] #title
        ysi1_l =  processed_rss['ysi_0'][1] # link
        # ysi 2nd article
        ysi2_t = processed_rss['ysi_1'][0] #title
        ysi2_l =  processed_rss['ysi_1'][1] # link
        # ysi 3rd Article
        ysi3_t = processed_rss['ysi_2'][0] #title
        ysi3_l =  processed_rss['ysi_2'][1] # link
        # ysi 1st article
        ysi4_t = processed_rss['ysi_3'][0] #title
        ysi4_l =  processed_rss['ysi_3'][1] # link
        # ysi 2nd article
        ysi5_t = processed_rss['ysi_4'][0] #title
        ysi5_l =  processed_rss['ysi_4'][1] # link

        prompt = f'In <p> formatting, give me a cyber intelligence & financial security intelligence executive summary based on every information provided:\n{processed_report_data}'
        openai.api_key = cfg.openai_api_key
        response = ai.GPT4(prompt)

        message = response['choices'][0]['message']['content']
    
        env = Environment(loader=FileSystemLoader('html'))
        template = env.get_template('report.html')
        html = template.render(logo=cfg.logo, DATETIME=today, YEETGPT_EXEC_SYNOPSIS=message,
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
        
        cur = conn.cursor()
        cur.execute(cfg.db_statement)
        receiver_emails = cur.fetchall()
        processed_emails = email_service.process_emails(receiver_emails)
        cur.close()
        conn.close()

        email_service.send(processed_emails, cfg, html, today)

    except Exception as e:
        # Handle exceptions here
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    """ scheduler = BlockingScheduler()
    scheduler.add_job(main, 'cron', day_of_week='mon', hour=13)
    scheduler.add_job(main, 'cron', day_of_week='fri', hour=13)
    scheduler.start() """
    main()
