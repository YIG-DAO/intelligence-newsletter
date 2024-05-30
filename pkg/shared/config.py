import os
from dotenv import load_dotenv

load_dotenv()

logo = os.getenv('LOGO_URL')

port = 587  # For starttls
smtp_server = os.getenv('SMTP_SERVER')

openai_api_key  = os.getenv('OPENAI_API_KEY')
sender_email = os.getenv('SMTP_SENDER')
smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')

# receiver emails
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('PG_USER')
db_pw = os.getenv('PG_PASSWORD')
db_statement = os.getenv('DB_STATEMENT')

# URL
ysi_feed = os.getenv('YSI_FEED')
sent_url = os.getenv('SENTIMENT_URL')
ins_url = os.getenv('INSIDER_URL')
insider_key = os.getenv('INSIDER_KEY')
insider_url = f"{ins_url}?api_key={insider_key}"
cont_url = os.getenv('CONTRACT_URL')
contract_key = os.getenv('CONTRACT_KEY')
contract_url = f"{cont_url}?api_key={contract_key}"
cve_url = os.getenv('CVE_URL')

url_list = [sent_url, contract_url, insider_url]
names = ['sentiment_url', "contract_url", "insider_url"]