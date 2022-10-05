from threading import Thread
import os
from flask import Flask
from system.utils import logger
from time import sleep
app = Flask('')

INFO = logger.LoggingType.INFO
WARN = logger.LoggingType.WARN
ERROR = logger.LoggingType.ERROR

logging = logger.LoggerInstance(INFO, "system.utils.run")

@app.route("/")
def home():
    return "The bot is alive!"

def run():
    logging.log("run", "Running Flask app on host 0.0.0.0 (port 8080)")
    app.run(host="0.0.0.0", port=8080) 
def start_lavalink():
    logging.log("start_lavalink","Starting Lavalink server trough `java -jar Lavalink.jar`")
    os.system("java -jar Lavalink.jar")
def run_lavalink(timeout=60.0):
    t = Thread(target=start_lavalink)
    t.start()
    logging.log("run_lavalink", f"Waiting {float(timeout)} seconds to prevent wavelink node errors", WARN)
    sleep(timeout)

def keep_alive():
    t = Thread(target=run)
    t.start()
    logging.log("keep_alive","KeepAlive server initialized.")
