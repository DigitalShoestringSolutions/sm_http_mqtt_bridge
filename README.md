# sm_http_mqtt_bridge
## Run
Run with Docker compose

## Usage
HTTP POSTs to http://<ip>:8080/<topic> with json payloads will be forwarded over MQTT on <topic>

so a POST of {"a":"b"} to http://<ip>:8080/1/2/3/4 will lead to {"a":"b"} being published on topic 1/2/3/4
