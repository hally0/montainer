# montainer

Running the program: 

First you need to create a montainer.ini file:

[GENERAL]
SYNCTIME = 3
DOWNTIME = 1
[PUSHBULLET]
TOKEN = INSERT PUSHBULLET TOKEN HERE

Then you can run the program through docker: 

docker run -it –rm –name montainer -d -v /var/run/docker.sock:/var/run/docker.sock -v /path/to/montainer.ini:/usr/src/app/montainer.ini hally0/montainer:latest
