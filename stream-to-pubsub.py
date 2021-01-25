from datetime import datetime
import json
import time
import tweepy
from tweepy.streaming import StreamListener
from google.cloud import secretmanager
from google.cloud import pubsub_v1

# Enter your GCP project info here
project_id = "twitter-296505"
project_number = "419512302408"
pub_sub_topic = "twitter"

# Define the list of terms to listen to
# search_terms = ["btc", "bitcoin"]
print("Please enter search terms here (separated by a semicolon): ")
print()
search_terms = input().split(";")
print()
print("Sounds good! Here's the list of search terms: [" + ", ".join(search_terms) + "]")
print()

# Pull in access keys for Twitter from Secret Manager
secret_client = secretmanager.SecretManagerServiceClient()
secret_dict = {}
secret_names = ["twitter-api-key", "twitter-api-secret", "twitter-access-token", "twitter-access-token-secret"]
for secret_name in secret_names:
    secret_dict[secret_name] = secret_client.access_secret_version({"name": \
        f"projects/{project_number}/secrets/{secret_name}/versions/latest"}).payload.data.decode("UTF-8")

# Authenticate to the Twitter API
auth = tweepy.OAuthHandler(secret_dict["twitter-api-key"], \
    secret_dict["twitter-api-secret"])
auth.set_access_token(secret_dict["twitter-access-token"], \
    secret_dict["twitter-access-token-secret"])

# Pub/Sub Config
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(f"{project_id}", f"{pub_sub_topic}")

# ???
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=False)

# Method to push messages to Pub/Sub
def write_to_pubsub(tweet):

    str_keys = ["id_str","in_reply_to_status_id_str",\
        "in_reply_to_user_id_str","lang","text"]
    int_keys = ["quote_count","reply_count","retweet_count","favorite_count"]
    dict_keys = ["coordinates","place","entities","user"]
    bool_keys = ["truncated"]

    processed_doc = {}

    try:
        processed_doc["created_at"] = datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y").isoformat()
        
        for key in str_keys:
            if key in tweet:
                processed_doc[key] = tweet[key]
            else:
                processed_doc[key] = "null"        

        for key in int_keys:
            if key in tweet:
                processed_doc[key] = tweet[key]
            else:
                processed_doc[key] = 0

        for key in dict_keys:
            if key in tweet:        
                processed_doc[key] = json.dumps(tweet[key])
            else:
                processed_doc[key] = "null"

        for key in bool_keys:
            if key in tweet:        
                processed_doc[key] = tweet[key]
            else:
                processed_doc[key] = False

    except Exception as e:
        print("Dict processing failed")
        print(e)
        raise                   
     
    try:
        # Publish data
        publisher.publish(topic_path, \
            data=json.dumps(processed_doc).encode("utf-8"), \
            tweet_id=str(processed_doc["id_str"]).encode("utf-8"))            

    except Exception as e:
        print("Publishing step failed")
        print(e)
        raise        

# Custom listener class
class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just pushes tweets to Pub/Sub
    """

    def __init__(self):
        super(StdOutListener, self).__init__()
        self._counter = 0

    def on_status(self, data):
        self._counter += 1
        write_to_pubsub(data._json)
        if self._counter == 1:    
            print(f"Found {self._counter} tweet so far!")        
        else:
            print(f"Found {self._counter} tweets so far!")        
        # if self._counter % 10 == 0:
        #     print(f"Found {self._counter} tweets so far!")        
        return True

    def on_error(self, status):
        print("Error found!")
        print("Status:")
        print(status)

# Start listening
print("Listening for tweets now")
print()
l = StdOutListener()
stream = tweepy.Stream(auth, l, tweet_mode="extended", is_async=True) # add 'is_async=True' so your connection isn't broken
stream.filter(track=search_terms)