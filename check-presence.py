import os
import json
import time
import argparse
import pytz
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from datetime import datetime

OUTPUT_DIR = "output"
CACHE_FILE = "ids-to-emails-cache.json"
TIME_ZONE = pytz.timezone('Europe/Madrid')
CALL_THROTLE_SEC = 0.5

load_dotenv()

parser = argparse.ArgumentParser(description='Accepts list of slack user emails')
parser.add_argument('emails', nargs='+', help='List of slack user emails')

emails = parser.parse_args().emails

slack_token=os.getenv('SLACK_TOKEN')
if not slack_token:
    raise ValueError("SLACK_TOKEN environment variable is not set")

client = WebClient(token=slack_token)

# Create output directory if not exist to keep CVS stats
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Directory {OUTPUT_DIR} created.")
else:
    print(f"Directory {OUTPUT_DIR} already exists.")

# Attempt to get locally cached emails -> slack ids mapping
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        emails_to_ids = json.load(f)
else:
    emails_to_ids = {}

# Resolve unkonwn emails
is_new_email = False

for email in emails:

    if email in emails_to_ids:
        continue;

    try:
        response = client.users_lookupByEmail(email=email)   

        if response['ok']:
            user_id = response['user']['id']
            emails_to_ids[email] = user_id
            print(f"Email {email} has been resolved to {user_id}")
            is_new_email = True
        else:
            print(f"Unable to get user id for {email}, response: {response}")
        
        time.sleep(CALL_THROTLE_SEC)
    except SlackApiError as e:
        print(f"User wasn't found, original error: {e.response['error']}")

# Update the mapping
if is_new_email:
    print("New emails discovered, updating local mapping file")
    with open(CACHE_FILE, "w") as f:
        json.dump(emails_to_ids, f)

# Start collecting presence to CSV file
file_path = OUTPUT_DIR + '/' + datetime.now(TIME_ZONE).strftime('%Y-%m-%d') + '.csv'
is_first_run = not os.path.exists(file_path)

heading = "date,time," + ','.join(emails)
print(heading)

try:
    add_time = True
    for email in emails:
        user_id = emails_to_ids[email]
        response = client.users_getPresence(user=user_id)
        if response['ok']:
            presence = response['presence']
            print(f"User {email} is {presence}")
            with open(file_path, 'a') as file:
                if is_first_run:
                    file.write(heading + "\n")
                    is_first_run = False
                if add_time:
                    file.write(datetime.now(TIME_ZONE).strftime('%Y-%m-%d') + "," +  datetime.now(TIME_ZONE).strftime('%H:%M') + ",")
                    add_time = False
                file.write(f"{1 if presence == 'active' else 0},")
        else:
            print(f"Error: {response['error']}")
        time.sleep(CALL_THROTLE_SEC)
    with open(file_path, 'a') as file:
        file.write("\n")
except SlackApiError as e:
    print(f"Error: {e.response['error']}")