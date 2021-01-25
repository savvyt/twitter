# Tweet stream

The point of this project is to build a tool that could be used to analyze the frequency and volume of tweets about specific topics. So, for example, if you wanted to see how many people are tweeting about #POTUS, you could use this repo as a guide to set up a data pipeline that retrieves tweets that include "POTUS" as a hashtag, performs some data transformations on that data, and then visualizes the results.

## Overall flow

This pipeline mainly relies on: the Twitter API, Python, and GCP. It takes data from the Twitter API and sends it to Pub/Sub via a Python script running on a VM. Pub/Sub messages are then delivered to BigQuery via Dataflow and, finally, visualized in DataStudio (this last part is still very much a work in progress).

## The process in detail

### Set up a VM
* Created Debian 10 VM (small, us-east-4a)
	* Make sure to allow access to all APIs (also add "Secret Manager Secret Accessor" to the Compute Engine default service account in IAM)
* Setup advanced packaging tool, checked for Python 3, and installed pip using the instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-debian-10)
* Script requires tweepy and Google secretmanager, so I installed those packages
	* Ran into a problem where secretmanager wouldn't finish installing (see link [here](https://github.com/grpc/grpc/issues/22815)). Once I upgraded pip (with "pip3 install --upgrade pip") the install finished quickly
# Also installed git with `sudo apt install git`

### Installed packages for Python script
* pip3 install tweepy
* pip3 install google-cloud-secret-manager
* pip3 install google-cloud-pubsub

## Troubleshooting

If you run into errors where your Dataflow job doesn't run, you should double check to make sure that the necessary Dataflow APIs have been enabled (using the command 'gcloud services enable dataflow.googleapis.com').

## Notes

To get this project off the ground, I initially borrowed heavily from here:

https://github.com/TDehaene/blogposts/tree/master/got_sentiment