Basic Flask app for testing local ELK logging.

# Running ELK Locally

```bash
git clone https://github.com/deviantony/docker-elk.git
```

See that repo's README for updated information, but it is generally simple if you already have our backend able to run locally.

From that repo's root:

```bash
docker-compose up
```

## Verify ELK is Running

LogStash: Visit [http://localhost:9600/](http://localhost:9600/) and you should see some configuration settings.

ElasticSearch: Visit [http://localhost:9200/](http://localhost:9200/) and you should see a response containing "You Know, for Search"

Kibana: Visit [http://localhost:5601/](http://localhost:5601/) and you should see a login page. Use credentials `elastic` and `changeme`

## Add Some Data

First, let's bring up Kibana to see the data come in. Here are two ways of seeing the logs come in. 

1) Stream.

[Go to Kibana](http://localhost:5601/). Click on "Observability". Then under the "Logs" sub-header (on the left) click on "Stream". Then hit the "Stream live" button.

2) Discover.

[Go to Kibana](http://localhost:5601/). Click on "Analytics", then "Discover". In the upper-right is the time window setter. Click on the calendar drop down and toggle on refresh, set to every 5 seconds or so.

Now lets send some data to LogStash to go to ElasticSearch and be discoverable in Kibana. According to the configuration `logstash.conf`(in `docker-elk/logstash/pipeline/`), Logstash is listening on port 50000 (50,000) for incoming TCP messages. So lets send something that-a-way. Use whatever tool you'd like. I like telnet (`brew install telnet` on OSX).

```bash
telnet localhost 50000
a log message approaches
it gets closer
and passes right by
```
And you should see these appear, along with metadata. Type Ctrl+`]` to exit.

# Local Python Flask to LogStash

A simple demo script is in `logstash.py` to show the connection between Python, Flask, and LogStash. We need just two packages via `pip`; `Flask` and `python-logstash`.


Copy the above and from that environment, `export FLASK_APP=sample.py` and then `flask run` and then in another terminal you can `curl localhost:5000` to hit your flask endpoint and log those messages. They will show up in Kibana shortly!

## A Better LogStash Message

The `python-logstash` package sends the log message as a JSON dict. We can have LogStash take those messages and expand it before sending it to ElasticSearch. Back in your `logstash.conf` file (in `docker-elk/logstash/pipeline/`), declare our input from tcp to be json as so:

``` text
tcp {
    port => 50000
    codec => "json"
}
```

If you re-hit your flask endpoint, you should see a bevy of new fields available to display or filter on in Kibana.

## 🚨 Troubleshooting 🚨

In python-logstash, you may need to change `'host': self.host,` to `'host': {'hostname': self.host},`