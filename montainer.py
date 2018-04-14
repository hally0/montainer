from montainer import eventutilities, notifier, config
import time
import threading
import logging
import signal
import sys
import docker
import datetime


def signal_handler(signal, frame):
    """ Signal handler for shutting down the program."""
    print("You pressed Ctrl+C! Shutting down.")
    events.close()
    logging.shutdown()
    sys.exit(0)


def check_event(e):
    """ This function checks if an event already exists within the event_list. If not, it will appends if it follow the
        the right criteria."""
    logging.debug("Checking event")
    event_id = e.get("id")
    event_status = e.get("status")

    if event_status == "stop" or event_status == "health_status: unhealthy":
        logging.debug(event_status)
        logging.debug("Appending event to list ")
        if not events_list.exist(e):
            events_list.append(e)

    if event_status == "start" or event_status == "health_status: healthy":
        for ev in events_list:
            if ev.get("id") == event_id:
                events_list.remove(ev)
                logging.debug("Removing event from list")


def check_time(e):
    """ This function calulates the difference in time between the event and actual time.
        If the container has been down for more than the DOWNTIME permits it will return True, else False."""
    now = datetime.datetime.now()
    event_time_hour = datetime.datetime.fromtimestamp(e.get("time")).strftime("%H")
    event_time_minute = datetime.datetime.fromtimestamp(e.get("time")).strftime("%M")
    event_time_seconds = datetime.datetime.fromtimestamp(e.get("time")).strftime("%S")

    event_time = (int(event_time_hour) * 3600) + int(event_time_seconds) + (int(event_time_minute) * 60)
    now_seconds = (now.hour * 3600) + (now.minute * 60) + now.second

    time_delta = now_seconds - event_time

    if time_delta >= _DOWNTIME or time_delta <= 0 - _DOWNTIME:
        return True
    return False


def get_events(events_generator):
    """This function reads from the event stream, and checks if an event exist or not."""
    logging.debug("Starting event streamer")

    for e in events_generator:
        check_event(e)

    logging.debug("exiting event streamer")


if __name__ == '__main__':
    # Import downtime and synctime from the configuration file.
    config_file = config.Config("montainer.ini")
    config_section = config_file.get_sections("GENERAL")
    _SYNCTIME = int(config_section["SYNCTIME"])
    _DOWNTIME = int(config_section["DOWNTIME"])
    # Making the loggin configuration
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s",
                        datefmt="%m-%d %H:%M",
                        )

    events_list = eventutilities.EventUtilities()
    # Filters for the event stream. TODO make it so users can configure it from the configuration file.
    filters = {"type": ["container"], "event": ["stop", "start", "health_status"]}
    client = docker.from_env()

    events = client.events(filters=filters, decode=True)

    signal.signal(signal.SIGINT, signal_handler)
    # Make a thread to read the event stream
    t = threading.Thread(name="Event generator", target=get_events, args=(events,))
    t.setDaemon(False)
    t.start()
    # This loops handles the event_list and will notify clients if the container downtime exceeds _DOWNTIME
    while True:
        for event in events_list:
            if check_time(event):
                title = events_list.event_title(event)
                body = events_list.event_general(event)
                if notifier.Notifier().send_pushbullet(title, body):
                    events_list.remove(event)
                    logging.debug("Successfully sent out notification. Removing (" + ") from the list.")
                else:
                    logging.debug("Couldn't send notification. Retrying until success.")
        time.sleep(_SYNCTIME)
