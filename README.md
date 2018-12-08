# montainer

This program monitors the container on the docker socket. If a container stops or fails a health test,
Montainer sends a notification trough selected outputs in the montainer.ini file.

Montainer supports Pushbullet, Pushover and Email. More notifiers will be implemented soon. 
Docker-compose is supported through searching the docker-compose id for each event.

Running the program: 

First you need to create a montainer.ini file. Example configuration:

```
[GENERAL]
SYNCTIME = 3
DOWNTIME = 60
 
[PUSHBULLET]
PB_TOKEN = Insert Pushbullet token here
 
[PUSHOVER]
PO_TOKEN = Insert Pushover token here
USER_TOKEN = Insert Pushover user token heree
 
[EMAIL]
SMTP_ADDRESS = Your SMTP address
SMTP_PORT = insert SMTP port here
PASSWORD = Your password
FROM = Send mail from
TO = Send mail to
TLS = true, if you want to use TLS
```
To use a notifier, fill the montainer.ini with the appropriate notifiers. If you want to only use Pushbullet,
 simply remove all the notifiers you don't use (Pushover, Email in this case). Your ini file should look like this:
```
[GENERAL]
SYNCTIME = 3
DOWNTIME = 60
[PUSHBULLET]
PB_TOKEN = Insert Pushbullet token here

```

SYNCTIME is measured in seconds, and it tells the program when to check for DOWNTIME.
DOWNTIME is measured in seconds, and it tells the program how long a container can be down before sending a notification.
In the example montainer.ini file, the program checks for DOWNTIME every 3 seconds. If one or more container have been down for more than
60 seconds, Montainer will send out notifications.

Afterwards, you can run the program through this docker command:
```
docker run --name montainer -d \
    -v /etc/localtime:/etc/localtime:ro \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /path/to/montainer.ini:/usr/src/app/montainer.ini \
    hally0/montainer:latest
```
Example docker-composer with Nginx health test:
```
services:
    montainer:
        image: "hally0/montainer"
        container_name: montainer
        volumes:
         - /etc/localtime:/etc/localtime:ro
         - /var/run/docker.sock:/var/run/docker.sock
         - /path/to/montainer.ini:/usr/src/app/montainer.ini
        restart: unless-stopped
    nginx:
        image: "nginx:alpine"
        container_name: nginx
        healthcheck:
          test: curl -sS http://127.0.0.1:80 || exit 1
          interval: 20s
          timeout: 5s
          retries: 3
```
