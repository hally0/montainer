# montainer

This program monitors the container on the docker socket. If a container stops or fails a health test,
Montainer sends a notification trough selected outputs in the montainer.ini file.

Montainer only support Pushbullet for now. More notifiers will be implemented soon. 

Running the program: 

First you need to create a montainer.ini file. Example configuration:

```
[GENERAL]
SYNCTIME = 3
DOWNTIME = 60
[PUSHBULLET]
TOKEN = INSERT PUSHBULLET TOKEN HERE
```

SYNCTIME is measured in seconds, and it tells the program when to check for DOWNTIME.
DOWNTIME is measured in seconds, and it tells the program how long a container can be down before sending a notification.
In the example montainer.ini file, the program checks for DOWNTIME every 3 seconds. If one or more container have been down for more than
60 seconds, Montainer will send out notifications.

Afterwards, you can run the program through this docker command:
```
docker run –name montainer -d \
    -v /etc/localtime:/etc/localtime:ro \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /path/to/montainer.ini:/usr/src/app/montainer.ini \
    hally0/montainer:latest
```