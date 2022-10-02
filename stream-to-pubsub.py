from datetime import datetime
from pytz import timezone
import json
import time
import tweepy
from tweepy.streaming import Stream
from google.cloud import secretmanager
from google.cloud import pubsub_v1

# To track how long the script successfully executes
script_start = datetime.now(timezone('UTC')).astimezone(timezone('US/Eastern'))
print()
print(f"Script start date and time: {script_start.strftime('%m/%d/%Y %H:%M:%S')}")

# Load GCP project details
with open("./project-specs.json", "r") as j:
    project_specs = json.loads(j.read())
    project_id = project_specs["project_id"]
    project_number = project_specs["project_number"]
    pub_sub_topic = project_specs["pub_sub_topic"]
    print()
    print("Loading GCP project details from 'project-specs.json'")
    print()

# Prompt the user for the terms they want to search
print("Enter search terms here (separated by a semicolon): ")
print()
search_terms = input().split(";")
print()
print("Sounds good! Let's start streaming.")
print()

# Pull in access keys for Twitter from GCP Secret Manager
secret_client = secretmanager.SecretManagerServiceClient()
secret_dict = {}
secret_names = ["twitter-api-key", "twitter-api-secret", "twitter-access-token", "twitter-access-token-secret"]
for secret_name in secret_names:
    secret_dict[secret_name] = secret_client.access_secret_version({"name": \
        f"projects/{project_number}/secrets/{secret_name}/versions/latest"}).payload.data.decode("UTF-8")

# Authenticate to the Twitter API
auth = tweepy.OAuthHandler(secret_dict["twitter-api-key"], secret_dict["twitter-api-secret"])
auth.set_access_token(secret_dict["twitter-access-token"], secret_dict["twitter-access-token-secret"])

# Pub/Sub Config
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(f"{project_id}", f"{pub_sub_topic}")

# ???
api = tweepy.API(auth, wait_on_rate_limit=True)

# Method to push messages to Pub/Sub
def write_to_pubsub(tweet):

    # Initialize results dict
    results_dict = {}

    # Keys to search within tweet
    keys_dict = {
    "str_keys": {"keys": ["id_str","in_reply_to_status_id_str", "in_reply_to_user_id_str","lang","text"], "null_val": "null"},
    "dict_keys": {"keys": ["coordinates","place","entities","user"], "null_val": "null"},
    "bool_keys": {"keys": ["truncated"], "null_val": False}
    }

    # Add keys and values to results to be send to Pub/Sub
    try:
        # Add the search term
        results_dict["search_terms"] = ";".join(search_terms)
        # Get the tweet creation date
        results_dict["created_at"] = datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y").isoformat()
    
        for key_group in keys_dict:
            for key in keys_dict[key_group]["keys"]:            
                if key in tweet:
                    if isinstance(tweet[key], dict):
                        results_dict[key] = json.dumps(tweet[key])
                    else:
                        results_dict[key] = tweet[key]
                else:
                    results_dict[key] = keys_dict[key_group]["null_val"]

    except Exception as e:
        print("Dict processing failed")
        print(e)
        raise                

    # Publish the encoded data to Pub/Sub     
    try:
        # Publish data
        publisher.publish(topic_path, \
            data=json.dumps(results_dict).encode("utf-8"), \
            tweet_id=str(results_dict["id_str"]).encode("utf-8"))            

    except Exception as e:
        print("Publishing failed")
        print(e)
        raise        

# Custom listener class
class StdOutListener(Stream):

    # Initialize
    def __init__(self):
        super(StdOutListener, self).__init__()
        self._counter = 0

    def on_status(self, data):
        self._counter += 1
        write_to_pubsub(data._json)
        if self._counter % 10000 == 0:
            print(f"Collected {self._counter} tweets as of {datetime.now(timezone('UTC')).astimezone(timezone('US/Eastern')).strftime('%m/%d/%Y %H:%M:%S')}")
        return True

    def on_error(self, status):
        print("Error found!")
        print("Status:")
        print(status)

# Start streaming
while True:
    try:
        print("Streaming in tweets now!")
        print()
        l = StdOutListener()
        stream = tweepy.Stream(auth, l, tweet_mode="extended", is_async=True, \
            retry_count=10, stall_warnings=True)
        stream.filter(track=search_terms)

    # Added to combat connection errors that tend to arise
    except ConnectionResetError as error:
        print(str(error))
        print()
        error_time = datetime.now(timezone('UTC')).astimezone(timezone('US/Eastern'))
        print(f"ConnectionResetError occurred at {error_time.strftime('%m/%d/%Y %H:%M:%S')}")
        continue

    except Exception as e:
        # Check to see how long script ran
        print()
        print("Listening halted!")
        script_end = datetime.now(timezone('UTC')).astimezone(timezone('US/Eastern'))
        print(f"Script end date and time: {script_end.strftime('%m/%d/%Y %H:%M:%S')}")
        diff = (script_end - script_start).total_seconds()
        hours = diff // 3600
        minutes = diff % 3600 // 60
        seconds = round(diff - (hours * 3600) - (minutes * 60), 2)
        print(f"Script ran for: {hours} hours, {minutes} minutes, and {seconds} seconds")
        print()

        # Inspect errors
        print("See error below:")
        print()
        print(e)
        raise 