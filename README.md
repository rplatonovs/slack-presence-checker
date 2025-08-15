# slack-presence-checker
Simple tool which allows to track presence of specific slack users. Once executed it  checks current presence for the list of slack user emails of your workspace and store the data into a simple CSV file. The data is structured in a way which makes it easy to import to an excel or Google sheets file and do simple math and visualisation.

I keept the implementation damn simple and not optimized for dealing with long list of emails. May be some day I invest some time to make it work with Slack websockets API and stop polling data for each account individually.

# Prerequisites
You need to have admin access to your slack Workspace in order to create a simple Slack app and generate an API access token for it. 

The app will only require to have `users:read` and `users:read.email` user token scopes. No other configuration is required.

Once app is created add the API access token to `SLACK_TOKEN` env variable on the machine you like to run the script Without this env variable the script fail to connect to Slack api.

# Installation
It's recommened to run the scrpit in a Python virtual environment

```
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

# Run the script
Once you activate the virtual enviornment and have the dependiencies installed you can call the script providing a list of emails for users you'd like to check current presence status

```
python3 check-presence.py john.doe@company.com alex.dev@company.com
```

The script needs to resolve each email to slack user id. Every time the script encounters a new email it stores it in a local `ids-to-emails-cache.json` (cache) file. It's done to avoid unnecessary calls to Slack API. 

The result of the execution will be a simple CSV file stored in `output` directory. The data will be appended to this file on each subsequent run of the script forming a simple table where user emails are on the top and presence will be marked as `1` - active or `0` - away in the rows below. The script will create a new file every new day using the current date as a filename.

# Usage recommendation
The best is to execute the script automatically every X minutes registering it with crontab. For this there is a suplimentary bash file which ensures environment configuration and triggers the execution of the script. **Important:** Before using `run_check_presence.sh` modify it to use your local directory paths and list of emails

Sample crontab configuration:
```
*/5 * * * * /root/scripts/run_check_presence.sh >> /root/scripts/cron.log 2>&1
```
