from montainer import notifier, eventutilities, config
import time
import threading
import logging
import signal
import sys
import docker
import datetime


def sigterm_handler(signal, frame):
    """ Signal handler for shutting down the program."""
    print("Shutting down the program gracefully")
    events.close()
    logging.shutdown()
    sys.exit(0)


def int_handler(signal, frame):
    """ Signal handler for shutting down the program."""
    print("Shutting down the program gracefully")
    events.close()
    logging.shutdown()
    threading.enumerate()
    logging.debug(sys.exit(0))


def check_event(e):
    """ This function checks if an event already exists within the event_list. If not, it will appends if it follow the
        the right criteria."""
    event_name = e.get("Actor")["Attributes"]['name']
    event_status = e.get("status")
    logging.debug("Checking event: Container name: {}, container status: {}".format(event_name, event_status))
    if event_status == "stop" or event_status == "health_status: unhealthy":
        logging.debug("Appending event to list ")
        if not events_list.exist_append(e):
            events_list.append(e)
            events_list.build_text_event(e)

    if event_status == "start" or event_status == "health_status: healthy":
        if events_list.exist_remove(e):
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
        thread_event_checker = threading.Thread(name="Event checker", daemon=True, target=check_event, args=(e,))
        thread_event_checker.start()
    logging.debug("exiting event streamer")


def notify_stack(notifier_stack):
    logging.debug("Notifier thread has started. Waiting 10 seconds to send out notifications")
    time.sleep(10)
    if len(notifier_list) > 1:
        title, body = notifier_list.build_test_event_list(notifier_list)
    else:
        title, body = notifier_list.build_text_event(notifier_list[0])
    if notifier.send_notifications(title, body):
        logging.debug("Successfully sent out notifications")
    notifier_list.clear()
    global notifier_thread
    notifier_thread = False


if __name__ == '__main__':
    # Import downtime and synctime from the configuration file.
    config_file = config.Config("montainer.ini")
    config_section = config_file.get_section("GENERAL")
    _SYNCTIME = int(config_section["SYNCTIME"])
    _DOWNTIME = int(config_section["DOWNTIME"])
    # Making the logging configuration
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s",
                        datefmt="%m-%d %H:%M",
                        )

    events_list = eventutilities.EventUtilities()
    events_list_test = eventutilities.EventUtilities()

    notifier_list = eventutilities.EventUtilities()
    eventutilities.set_ip()

    # Filters for the event stream. TODO make it so users can configure it from the configuration file.
    filters = {"type": ["container"], "event": ["stop", "start", "health_status"]}
    client = docker.from_env()

    events = client.events(filters=filters, decode=True)

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, int_handler)

    notifier_thread = False

    # Make a thread to read the event stream
    thread_generator = threading.Thread(name="Event generator", target=get_events, daemon=True, args=(events,))
    thread_generator.start()

    # This loops handles the event_list and will notify clients if the container downtime exceeds _DOWNTIME
    while True:
        for event in events_list:
            if check_time(event):
                logging.debug("{} has been down for more than: {}s. Appending event to notifier stack".format(
                    event.get("Actor")["Attributes"]["name"], _DOWNTIME))
                notifier_list.append(event)
                if not notifier_thread:
                    thread_notifier = threading.Thread(name="Notifier", target=notify_stack, daemon=True, args=(event,))
                    thread_notifier.start()
                    notifier_thread = True
                events_list.remove(event)
        time.sleep(_SYNCTIME)
