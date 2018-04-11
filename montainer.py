from montainer import eventutilities, notifier, config
import time
import threading
import logging
import signal
import sys
import docker
import datetime


def signal_handler(signal, frame):
    print('You pressed Ctrl+C! Shutting down.')
    events.close()
    logging.shutdown()
    sys.exit(0)


def check_event(event):
    logging.debug('Checking event')
    event_id = event.get('id')
    event_status = event.get('status')

    if event_status == 'stop' or event_status == "health_status: unhealthy":
        logging.debug(event_status)
        logging.debug('Appending event to list ')
        if not events_list.exist(event):
            events_list.append(event)

    if event_status == 'start' or event_status == "health_status: healthy":
        for ev in events_list:
            if ev.get('id') == event_id:
                events_list.remove(ev)
                logging.debug('Removing event from list')


def notify(event):
    title = events_list.event_title(event)
    body = events_list.event_general(event)
    notifier.Notifier().send_pushbullet(title, body)


def check_time(event):
    now = datetime.datetime.now()
    event_time = datetime.datetime.fromtimestamp(event.get('time')).strftime("%M")
    if (now.minute - int(event_time)) >= _DOWNTIME:
        return True
    return False


def get_events(events_generator):

    logging.debug('Starting event streamer')

    for event in events_generator:
        check_event(event)

    logging.debug('exiting event streamer')


if __name__ == '__main__':
    config_file = config.Config('montainer.ini')
    config_section = config_file.get_sections('GENERAL')
    _SYNCTIME = int(config_section['SYNCTIME'])
    _DOWNTIME = int(config_section['DOWNTIME'])

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                        datefmt='%m-%d %H:%M',
                        )
    events_list = eventutilities.EventUtilities()

    filters = {'type': ['container'], 'event': ['stop', 'start', 'health_status']}
    client = docker.from_env()

    events = client.events(filters=filters, decode=True)

    signal.signal(signal.SIGINT, signal_handler)

    t = threading.Thread(name='Event generator', target=get_events, args=(events,))
    t.setDaemon(False)
    t.start()

    while True:
        for e in events_list:
            if check_time(e):
                notify(e)
                events_list.remove(e)
                logging.debug('Removing (' + ') from the list.')
        time.sleep(_SYNCTIME)
