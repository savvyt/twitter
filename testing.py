import tweepy
from google.cloud import secretmanager

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

print("secret_dict")
print(secret_dict)

# Authenticate to the Twitter API
auth = tweepy.OAuthHandler(secret_dict["twitter-api-key"], \
    secret_dict["twitter-api-secret"])
auth.set_access_token(secret_dict["twitter-access-token"], \
    secret_dict["twitter-access-token-secret"])

# Authenticate to the Twitter API
auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)

api = tweepy.API(auth)

print("Performing simple test!")
# Simple test
public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)

print()
print("Performing streaming test!")
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