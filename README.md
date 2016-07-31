# Bee Oberservation - Guide
This repository contains source code to power a Raspberry Pi with a DHT22
temperature and humidity sensor to monitor the health of a bee hive. Besides the
measurements, the source code handles a live stream to YouTube with sound, so
you can have a look at the hives at all point at time.

Furthermore the following describes how to setup the system, general tips and a
references other tutorials.

Resources:
[Adafruit IO Python Client](https://github.com/adafruit/io-client-python)

## Get started

There are some dependencies that needs to be installed globally. Therefore please
run ``pip install -r requirements.txt``.

### Setup Adafruit DHT22 library
Clone the repository from
[Adafruit Python DHT](https://github.com/adafruit/Adafruit_Python_DHT) and
follow the instructions in the README.md.

### Setup program
First we need to place the main.py as ``bee-observation`` in ``usr/bin`` to run it
from the command line. Afterwards it's important to create the logging folder with
``mkdir -r /var/log/bee-observation``.


### Install as a service
At startup we want to also run the bee observation, therefore a systemd file
needs to be placed into the ``/etc/systemd/system`` folder. The file contains a
description of the service:

```
[Unit]
Description=Measure temperature and humidity with dht22 and send to Adafruit IO
After=multi-user.target

[Service]
Type=idle
Environment=ADAFRUIT_API_USERNAME=YOUR_USERNAME
Environment=ADAFRUIT_API_KEY=YOUR_KEY
ExecStart=/usr/bin/bee-observation           
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Next we need to enable the service:
```sh
systemctl enable bee-observation.service
```
We can start the service right away with:
```sh
systemctl start bee-observation.service
```
If you want to follow the logs:
```sh
tail -f /var/log/bee-observation/main.log
```
