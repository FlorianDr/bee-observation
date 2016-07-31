#!/usr/bin/env python

import Adafruit_DHT
import logging
import os
import sys

from Adafruit_IO import MQTTClient, AdafruitIOError
from time import sleep

logging.basicConfig(filename='/var/log/bee-observation/main.log', level=logging.INFO)
logger = logging.getLogger('main.py')

DHT_TYPE = Adafruit_DHT.DHT22
DHT_PIN = 4

TIME_INTERVAL = 10
TIME_INTERVAL_FEED = 'time_interval'

try:
    IO_USERNAME = os.environ['ADAFRUIT_API_USERNAME']
    IO_KEY = os.environ['ADAFRUIT_API_KEY']
except KeyError as e:
    logger.error('Adafruit credentials are not defined: {}'.format(e))
    sys.exit(1)

def connected(client):
    logger.info('Connected to Adafruit IO server')
    client.subscribe(TIME_INTERVAL_FEED)

def disconnected(client):
    retries = 1
    logger.warning('Disconnected from Adafruit IO server')
    while client.is_connected() is False:
        logger.info('Retry #{} to connect'.format(retries))
        client.connect()
        retries = retries + 1
        sleep(15)

def message(client, feed_id, payload):
    logger.debug('Feed {0} received new value: {1}'.format(feed_id, payload))
    if feed_id is TIME_INTERVAL_FEED:
        logger.info('Set sampling interval to {}'.format(payload))
        TIME_INTERVAL = payload

def measure():
    logger.debug('measure is called')
    try:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)
    except RuntimeError as e:
        logger.error('Error reading sensor data: {}'.format(e))
    return humidity, temperature

def publish(client, feed_id, value):
    logger.debug('publish is called')
    if feed_id is not None and value is not None:
        try:
            logger.debug('Publish {} to {}'.format(value, feed_id))
            client.publish(feed_id, value)
        except AdafruitIOError as e:
            logger.error('Error sending {} to {} : {}'.format(value, feed_id, e))

def main():

    # Create a mqttclient
    client = MQTTClient(IO_USERNAME, IO_KEY)

    # Assign handlers for events
    client.on_connect    = connected
    client.on_disconnect = disconnected
    client.on_message    = message

    logger.debug('Connect to Adafruit IO server')
    client.connect()

    logger.debug('Start background thread for messaging')
    client.loop_background()

    while True:
        humidity, temperature = measure()
        if humidity is not None and temperature is not None:
            logger.info('Temperature={0:0.1f}, Humidity={1:0.1f}'.format(humidity, temperature))
            publish(client, 'humidity', humidity)
            publish(client, 'temperature', temperature)
        sleep(TIME_INTERVAL)

if __name__ == '__main__':
    main()
