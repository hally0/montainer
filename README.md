# montainer

Running the program: 

First you need to create a montainer.ini file:

[GENERAL] <br />
SYNCTIME = 3 <br />
DOWNTIME = 1 <br />
[PUSHBULLET] <br />
TOKEN = INSERT PUSHBULLET TOKEN HERE <br />

Then you can run the program through docker: 

docker run -it –rm –name montainer -d -v /var/run/docker.sock:/var/run/docker.sock -v /path/to/montainer.ini:/usr/src/app/montainer.ini hally0/montainer:latest
