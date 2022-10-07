from threading import Thread
import os
from flask import Flask
from utils import logger
from time import sleep
app = Flask('')

logging = logger.Logger().get("utils.run")

@app.route("/")
def home():
    return "The bot is alive!"

def run():
    logging.info("run", "Running Flask app on host 0.0.0.0 (port 8080)")
    app.run(host="0.0.0.0", port=8080) 
def start_lavalink():
    logging.info("start_lavalink","Starting Lavalink server trough `java -jar Lavalink.jar`")
    os.system("java -jar Lavalink.jar")
def run_lavalink(timeout=60.0):
    t = Thread(target=start_lavalink)
    t.start()
    logging.warn("run_lavalink", f"Waiting {float(timeout)} seconds to prevent wavelink node errors")
    sleep(timeout)

def keep_alive():
    t = Thread(target=run)
    t.start()
    logging.info("keep_alive","KeepAlive server initialized.")
