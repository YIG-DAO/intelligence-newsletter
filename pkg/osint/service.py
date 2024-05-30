import json
import feedparser
import requests
import time

def gov_contracts_process(contract_url):
    """
    Fetches government contracts data from the specified URL and processes it.

    Args:
        contract_url (str): The URL to fetch the government contracts data from.

    Returns:
        list: A list of processed government contracts.

    Raises:
        requests.exceptions.RequestException: If an error occurs while fetching the data.
    """
    print("> Fetching Government Contracts")
    processed_gov_contracts = {}
    try:
        response = requests.get(contract_url)
        response.raise_for_status() # check for any request errors
        preprocessed = response.json()
        result = []
        filter = 0
        for i in preprocessed['response'][:200]:
            temp = i['Amount']
            if temp > 250000:
                filter += 1
                result.append(i)
            if filter == 3:
                break
        processed_gov_contracts = result
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the government contracts data: {str(e)}")
        return None
    return processed_gov_contracts

def insider_trades_process(insider_url):
    """
    Fetches insider trades data from the specified URL and processes it.

    Args:
        insider_url (str): The URL to fetch the insider trades data from.

    Returns:
        list: A list of processed insider trades.

    Raises:
        requests.exceptions.RequestException: If an error occurs while fetching the data.
    """
    print("> Fetching Insider Trades")
    insider_trades = {}
    try:
        response = requests.get(insider_url)
        response.raise_for_status() # check for any request errors
        preprocessed = response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the insider trades data: {str(e)}")
        return None
    temp = preprocessed['response'][:3] # Top 3 insider
    insider_trades = []
    for i in temp:
        insider_trades.append(i)
    return insider_trades

def cve_process(cve_url):
    """
    Fetches CVE (Common Vulnerabilities and Exposures) data from the specified URL and processes it.

    Args:
        cve_url (str): The URL to fetch the CVE data from.

    Returns:
        list: A list of processed CVE information.

    Raises:
        requests.exceptions.RequestException: If an error occurs while fetching the data.
    """
    print("> Fetching CVE")
    processed_cve = {}
    try:
        response = requests.get(cve_url) # more robust request
        response.raise_for_status() # check for any request errors
        preprocessed = response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the CVE data: {str(e)}")
    # Targeting the latest
    check = []
    for i in preprocessed['vulnerabilities']:
        well = i['cve']['lastModified']
        check.append(well)
    check.sort(reverse=True)

    result = []
    for date in check[:3]:
        for i in preprocessed['vulnerabilities']:
            well = i['cve']['lastModified']
            if date == well:
                id = i['cve']['id']
                link = i['cve']['references'][0]['url']
                data = {'id': id, 'link' : link}
                result.append(data)

    processed_cve = result

    return processed_cve


def sent_process(sent_url):
    """
    Fetches sentiment data from the specified URL and processes it.

    Args:
        sent_url (str): The URL to fetch the sentiment data from.

    Returns:
        list: A list of processed sentiment data.

    Raises:
        Exception: If an error occurs while fetching the data.
    """
    try:
        print("> Fetching Sentiment")
        result = []
        response = requests.get(sent_url)
        preprocessed = response.json()
        for i in preprocessed['response'][:3]:
            symbol = i['symbol']
            sent_score = i['sentiment']
            last_sent = i['lastSentiment']
            data = {'symbol': symbol, 'sent_score':sent_score, 'last_sentiment':last_sent}
            result.append(data)
        processed_sent = result
        return processed_sent
    except Exception as e:
        print(f"An error occurred while fetching the sentiment data: {str(e)}")
        return None

def rss_process(ysi_feed):
    """
    Fetches RSS feed data from the specified URL and processes it.

    Args:
        ysi_feed (str): The URL to fetch the RSS feed data from.

    Returns:
        dict: A dictionary of processed RSS feed data.

    Raises:
        Exception: If an error occurs while fetching the data.
    """
    try:
        print("> Fetching RSS Feed")
        processed_rss = {}
        processed_ysi= feedparser.parse(ysi_feed).entries
        processed = processed_ysi[:5]
        for i,each in enumerate(processed):
            ysi = []
            ysi.append(each['title'])
            ysi.append(each['link'])
            key = f'ysi_{i}'
            processed_rss[key] = ysi

        return processed_rss
    except Exception as e:
        print(f"An error occurred while fetching the RSS feed: {str(e)}")
        return None

def extract_data(rss_url, sentiment_url, gov_contracts_url, insider_trades_url, cve_url):
    """
    Extracts data from various sources and returns the processed data.

    Returns:
        JSON: A JSON object containing the processed data from different sources.
            - processed_rss: Processed RSS data.
            - processed_sentiment: Processed sentiment data.
            - processed_gov_contracts: Processed government contracts data.
            - processed_insider_trades: Processed insider trades data.
            - processed_cve: Processed CVE data.
    """
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            processed_rss = rss_process(rss_url)
            processed_sentiment = sent_process(sentiment_url)
            processed_gov_contracts = gov_contracts_process(gov_contracts_url)
            processed_insider_trades = insider_trades_process(insider_trades_url)
            processed_cve = cve_process(cve_url)
            report_data = {
                "gov_contracts": processed_gov_contracts,
                "insider_trades": processed_insider_trades,
                "cve": processed_cve,
                "sentiment": processed_sentiment,
                "rss": processed_rss
            }
            return report_data
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the data: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries exceeded. Unable to fetch the data.")
                return None