# Tweet stream

The point of this project is to build a tool using Python and GCP that can be used to analyze the frequency and volume of tweets about specific topics. So, for example, if you wanted to see how many people are tweeting about #POTUS, you could use this repo as a guide to set up a data pipeline that retrieves tweets that include "POTUS" as a hashtag, performs some data transformations on that data, and then visualizes the volume of those tweets over time.

## Overall flow

This pipeline mainly relies on: the Twitter API, Python, and GCP. It takes data from the Twitter API and sends it to Pub/Sub via a Python script running on a VM. Pub/Sub messages are then delivered to BigQuery via Dataflow and, finally, visualized in DataStudio (this last part is still very much a work in progress).

## The process

I'm including lots of detail here to try and help make the setup process faster for others.

### Set up and run Python script on VM

First you need to set up a VM that will run the tweet streaming script. Here's what I did:

* Created a Debian 10 VM (size: small, zone: us-east-4a)
	* Make sure to allow access to all APIs (also add "Secret Manager Secret Accessor" to the Compute Engine default service account in IAM)
* On the VM, setup a packaging tool, check for Python 3, and install pip (instructions posted [here](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-debian-10))
* Then install tweepy and Google secretmanager
	* `pip3 install tweepy`
	* `pip3 install google-cloud-secret-manager`
	* `pip3 install google-cloud-pubsub`
	* Note: I ran into a problem where secretmanager wouldn't finish installing (see link [here](https://github.com/grpc/grpc/issues/22815)). Once I upgraded pip (with "pip3 install --upgrade pip") the install finished quickly.
* Finally, I installed git so I could pull directly from this repo (`sudo apt install git`)

### Run the script

Try running the script to make sure that it actually works on the VM. If it does, then move on to the next part...

### Setup a Dataflow job

Now you need a Dataflow job to take the messages that Pub/Sub will receive while the streaming script is running and send those messages to BigQuery. To do that, you can use a GCP template for connecting Pub/Sub to BigQuery:

(Photo of template)

Note that you'll need a GCS bucket to temporarily store files coming in from Dataflow and you'll also need an empty table in BigQuery with the appropriate schema to receive the streaming data.

Once those are ready, you can start the Dataflow job and run the script from your VM. Wait a few minutes and you should start to see rows populating in your BigQuery table:

(Photo of BQ table)

### Visualization

(To do)

## Current to dos

This repo is very much a work in progress. I still need to clean up and consolidate the code, add more details about the pipeline process, and improve data visualization.

## Troubleshooting

If you run into errors where your Dataflow job doesn't run, you should double check to make sure that the necessary Dataflow APIs have been enabled (using the command 'gcloud services enable dataflow.googleapis.com').

## Notes

To get this project off the ground, I initially borrowed heavily from here:

https://github.com/TDehaene/blogposts/tree/master/got_sentiment