## Current to do list

* Short term
	* Visualize data in a continuous, non-static fashion.
	* Make script robust to timeout issues.
	* Need to consolidate the first part of the `write_to_pubsub` function. Currently redundant.
	* Need to make `stream-to-pubsub.py` search within tweets using lowercase tweet text (so that all results are captured, not just exact string matches)
	* Make it possible to separate query strings and organize results in BQ based on query string matches (each row corresponds to a match with a given query paramater in the list)
	* Print out stopwatch info if you kill scrip early with ctrl + c (see link [here](https://stackoverflow.com/questions/37378185/handle-ctrl-c-in-python-cmd-module))

* Long term	
	* Analyze tweet sentiment in real time using NLP