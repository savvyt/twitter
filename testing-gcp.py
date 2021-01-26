import tweepy
from google.cloud import secretmanager
import ntplib
from datetime import datetime, timezone
from time import ctime

# Checking the time
c = ntplib.NTPClient()
# Provide the respective ntp server ip in below function
response = c.request('uk.pool.ntp.org', version=3)
response.offset
print()
print("Time check!")
print(datetime.fromtimestamp(response.tx_time, timezone.utc))    
print()

# Enter your GCP project info here
project_id = "twitter-296505"
project_number = "419512302408"

# Pull in access keys for Twitter from GCP Secret Manager
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

api = tweepy.API(auth)

print("Simple batch API call")
print()
# Simple test
public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)
print()

print("Streaming API call test")
print()
# Streaming test
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

    def on_error(self, status):
        print("Error found!")
        print("Status:")
        print(status)        

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = auth, listener=myStreamListener)
myStream.filter(track=['python'])