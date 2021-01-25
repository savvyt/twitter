import datetime
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
search_terms = ["btc", "bitcoin"]

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

# # Method to push messages to Pub/Sub
# def write_to_pubsub(data):
#     try:
#         if data["lang"] == "en":     

#             # # V1 for sending messages to Pub/Sub
#             # publisher.publish(topic_path, data=json.dumps({
#             #     "id": data["id_str"],
#             #     "posted_at": data["created_at"],
#             #     "text": data["text"]
#             # }).encode("utf-8"), tweet_id=str(data["id_str"]).encode("utf-8"))            

#             # Dump everything
#             v2 = json.dumps(data).encode("utf-8")

#             publisher.publish(topic_path, data=v2, \
#                 tweet_id=str(data["id_str"]).encode("utf-8"))            

#     except Exception as e:
#         raise

# Method to push messages to Pub/Sub
def write_to_pubsub_v2(tweet):

    str_keys = ['created_at','id_str','in_reply_to_status_id_str',\
        'in_reply_to_user_id_str','lang','text']
    int_keys = ['quote_count','reply_count','retweet_count','favorite_count']
    dict_keys = ['coordinates','place','entities','user']
    bool_keys = ['truncated']

    # keys_dict = {'str': {'null_type': 'none', \
    #     'vals': ['created_at','id_str','in_reply_to_status_id_str',\
    #     'in_reply_to_user_id_str','lang','text']},
    #     'bool': {'null_type': 'none', \
    #     'vals': ['truncated']},

    #     }

    results_dict = {}

    try:
        for key in str_keys:
            if key in tweet:
                results_dict[key] = tweet[key]
            else:
                results_dict[key] = "null"        

        for key in int_keys:
            if key in tweet:
                results_dict[key] = tweet[key]
            else:
                results_dict[key] = 0

        for key in dict_keys:
            if key in tweet:        
                results_dict[key] = json.dumps(tweet[key])
            else:
                results_dict[key] = "null"

        for key in bool_keys:
            if key in tweet:        
                results_dict[key] = tweet[key]
            else:
                results_dict[key] = False

    except Exception as e:
        print("Dict processing failed")
        print(e)
        raise                  

    # # if results_dict['coordinates'] != "null":
    # print("results_dict:")
    # print(results_dict)
    # print()   
     
    try:
        if results_dict["lang"] == "en":     

            # # V1 for sending messages to Pub/Sub
            # publisher.publish(topic_path, data=json.dumps({
            #     "id": data["id_str"],
            #     "posted_at": data["created_at"],
            #     "text": data["text"]
            # }).encode("utf-8"), tweet_id=str(data["id_str"]).encode("utf-8"))            

            # Dump everything
            publisher.publish(topic_path, \
                data=json.dumps(results_dict).encode("utf-8"), \
                tweet_id=str(results_dict["id_str"]).encode("utf-8"))            

    except Exception as e:
        print("Publishing step failed")
        print(e)
        raise        

# # Method to format a tweet from tweepy
# def reformat_tweet(tweet):
#     # x = tweet

#     # results_dict = {
#     #     "id": x["id"],
#     #     "lang": x["lang"],
#         # "retweeted_id": x["retweeted_status"]["id"] if "retweeted_status" in x else None,
#         # "favorite_count": x["favorite_count"] if "favorite_count" in x else 0,
#         # "retweet_count": x["retweet_count"] if "retweet_count" in x else 0,
#         # "lat": x["coordinates"]["coordinates"][0] if x["coordinates"] else 0,
#         # "lng": x["coordinates"]["coordinates"][1] if x["coordinates"] else 0,
#         # "place": x["place"]["country_code"] if x["place"] else None,
#         # "user_id": x["user"]["id"],
#         # "created_at": time.mktime(time.strptime(x["created_at"], "%a %b %d %H:%M:%S +0000 %Y"))
#     # }

#     # if x["entities"]["hashtags"]:
#     #     results_dict["hashtags"] = [{"text": y["text"], "startindex": y["indices"][0]} for y in
#     #                                  x["entities"]["hashtags"]]
#     # else:
#     #     results_dict["hashtags"] = []

#     # if x["entities"]["user_mentions"]:
#     #     results_dict["usermentions"] = [{"screen_name": y["screen_name"], "startindex": y["indices"][0]} for y in
#     #                                      x["entities"]["user_mentions"]]
#     # else:
#     #     results_dict["usermentions"] = []

#     # if "extended_tweet" in x:
#     #     results_dict["text"] = x["extended_tweet"]["full_text"]
#     # elif "full_text" in x:
#     #     results_dict["text"] = x["full_text"]
#     # else:
#     #     results_dict["text"] = x["text"]

#     str_keys = ['created_at','id_str','in_reply_to_status_id_str',\
#         'in_reply_to_user_id_str','lang','text']
#     bool_keys = ['truncated']
#     dict_keys = ['coordinates','place','entities','user']
#     int_keys = ['quote_count','reply_count','retweet_count','favorite_count']

#     # keys_dict = {'str': {'null_type': 'none', \
#     #     'vals': ['created_at','id_str','in_reply_to_status_id_str',\
#     #     'in_reply_to_user_id_str','lang','text']},
#     #     'bool': {'null_type': 'none', \
#     #     'vals': ['truncated']},

#     #     }

#     results_dict = {}

#     for key in str_keys:
#         if key in tweet:
#             results_dict[key] = tweet[key]
#         else:
#             results_dict[key] = "None"        

#     for key in int_keys:
#         if key in tweet:
#             results_dict[key] = tweet[key]
#         else:
#             results_dict[key] = 0

#     for key in dict_keys:
#         if key in tweet:        
#             results_dict[key] = json.dumps(tweet[key])
#         else:
#             results_dict[key] = "None"

#     # if results_dict['coordinates'] != "null":
#     print("results_dict:")
#     print(results_dict)
#     print()

#     # # try:
#     # if x['place']:
#     #     print('created_at: ' + x['created_at'])
#     #     print('id_str: ' + x['id_str'])
#     #     print('text: ' + x['text'])    
#     #     print('lang: ' + x['lang'])
#     #     print('place: ' + x['place'])            
#     #     print('coordinates: ' + x['coordinates'])
#     #     print('retweeted_status: ' + x['retweeted_status'])
#     #     print('quote_count: ' + x['quote_count'])
#     #     print('reply_count: ' + x['reply_count'])
#     #     print('retweet_count: ' + x['retweet_count'])
#     #     print('favorite_count: ' + x['favorite_count'])
#     #     print('entities: ' + x['entities'])
#     #     print('truncated: ' + x['truncated'])
#     #     print('in_reply_to_status_id_str: ' + x['in_reply_to_status_id_str'])
#     #     print('in_reply_to_user_id_str: ' + x['in_reply_to_user_id_str'])            
#     #     print()
#     # # except:
#     # #     pass        
    
#     return results_dict

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
        write_to_pubsub_v2(data._json)
        return True

    def on_error(self, status):
        print("Error found!")
        print("Status:")
        print(status)
        if status == 420:
            print("Hitting rate limit")
            return False

# Start listening
print("Listening for tweets now")
l = StdOutListener()
stream = tweepy.Stream(auth, l, tweet_mode="extended", is_async=True)
stream.filter(track=search_terms)