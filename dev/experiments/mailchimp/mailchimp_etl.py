import os
import sys
import requests
import datetime
sys.path.append('./')
import cx_Oracle
import mailchimp_marketing as MailchimpMarketing

# Replace these with your actual MailChimp API key and list of campaign IDs
MAILCHIMP_API_KEY  = "xxx"
MAILCHIMP_SERVER  = "us1"

client = MailchimpMarketing.Client()
client.set_config({
    "api_key": MAILCHIMP_API_KEY,
    "server": MAILCHIMP_SERVER
})

def mailchimp_extractor_campaign():
    response = client.campaigns.list(count=1000)
    campaigns = []
    for campaign in response["campaigns"]:
        campaigns.append(campaign["id"])
    return campaigns

def get_mailchimp_data(api_key, campaign_id):
    url = f"https://us1.api.mailchimp.com/3.0/reports/{campaign_id}/email-activity?count=1000&offset=0"
    headers = {
        "Authorization": f"apikey {api_key}",
    }
    response = requests.get(url, headers=headers)
    return response.json()

def insert_data_into_oracle(data):
    data_to_insert = []
    # Establish a connection to the Oracle database
    with open('D:\contain-freemium\dev\ds_infra\ds_infra.env') as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value
    user = os.environ.get("USER")
    host = os.environ.get("HOST")
    service = os.environ.get("SERVICE")
    port = os.environ.get("PORT")
    password = os.environ.get("PASSWORD")

    conn = cx_Oracle.connect(
        user=user,
        password=password,
        dsn=f"{host}:{port}/{service}",
    )
    cursor = conn.cursor()

    for email in data['emails']:
        ORDER_ID = email['campaign_id']
        CUSTOMER_ID = email['email_id']
        for activity in email['activity']:
            action = activity['action']
            timestamp_str = activity['timestamp']  # Assuming 'timestamp' is a string in ISO 8601 format
            timestamp = datetime.datetime.fromisoformat(timestamp_str[:-6])  # Remove the timezone information
            data_to_insert.append(("1",ORDER_ID, CUSTOMER_ID, action, timestamp))
    query = 'INSERT INTO TEMP_RFM_ORDER_DATA (ACCOUNT_ID, ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_PURCHASE_TIMESTAMP ) VALUES (:1, :2, :3, :4, :5)'
    cursor.executemany(query, data_to_insert)

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    campaigns = mailchimp_extractor_campaign()
    print(f"Found {len(campaigns)} campaigns")
    for campaign_id in campaigns:
        mailchimp_data = get_mailchimp_data(MAILCHIMP_API_KEY, campaign_id)
        insert_data_into_oracle(mailchimp_data)
        print(f"Data inserted successfully for Campaign ID: {campaign_id}")
    print("All data inserted successfully into the Oracle database.")