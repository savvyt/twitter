# Tweet stream

WIP 

Borrowed heavily from here:

https://github.com/TDehaene/blogposts/tree/master/got_sentiment

## Setting up VM
* Created Debian 10 VM (small, us-east-4a)
	* Make sure to allow access to all APIs (also add "Secret Manager Secret Accessor" to the Compute Engine default service account in IAM)
* Setup advanced packaging tool, checked for Python 3, and installed pip using the instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-debian-10)
* Script requires tweepy and Google secretmanager, so I installed those packages
	* Ran into a problem where secretmanager wouldn't finish installing (see link [here](https://github.com/grpc/grpc/issues/22815)). Once I upgraded pip (with "pip3 install --upgrade pip") the install finished quickly
# Also installed git with `sudo apt install git`

## Installed packages for Python script
* pip3 install tweepy
* pip3 install google-cloud-secret-manager
* pip3 install google-cloud-pubsub

## More troubleshooting

If you run into errors where your Dataflow job doesn't run, you should double check to make sure that the necessary Dataflow APIs have been enabled (using the command 'gcloud services enable dataflow.googleapis.com').