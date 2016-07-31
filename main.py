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
BUFFER_SIZE = 3

try:
    IO_USERNAME = os.environ['ADAFRUIT_API_USERNAME']
    IO_KEY = os.environ['ADAFRUIT_API_KEY']
except KeyError as e:
    logger.error('Adafruit credentials are not defined: {}'.format(e))
    sys.exit(1)

def connected(client):
    logger.info('Connected to Adafruit IO server')

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

    temp_buffer = []
    hum_buffer = []
    while True:
        humidity, temperature = measure()
        if humidity is not None and temperature is not None:
            logger.info('Temperature={0:0.1f}, Humidity={1:0.1f}'.format(temperature, humidity))
            temp_buffer.append(temperature)
            hum_buffer.append(humidity)

        # Send median of last three records
        if len(temp_buffer) == BUFFER_SIZE:
            temp_buffer = sorted(temp_buffer)
            temp_median = temp_buffer[BUFFER_SIZE // 2]
            temp_median = round(temp_median, 1)
            logger.debug('Rounded median of temp_buffer({}) is {}'.format(temp_buffer, temp_median))
            publish(client, 'temperature', temp_median)
            temp_buffer = []

        # Send median of last three records
        if len(hum_buffer) == BUFFER_SIZE:
            hum_buffer = sorted(hum_buffer)
            hum_median = hum_buffer[BUFFER_SIZE // 2]
            hum_median = round(hum_median, 1)
            logger.debug('Rounded median of hum_buffer({}) is {}'.format(hum_buffer, hum_median))
            publish(client, 'humidity', hum_median)
            hum_buffer = []

        sleep(TIME_INTERVAL)

if __name__ == '__main__':
    main()
