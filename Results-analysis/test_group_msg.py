from __future__ import with_statement
from datetime import datetime as dt
import concurrent.futures
import os
import time
import pandas as pd
from flask import Flask, request, send_file
from flask_restful import Api
import requests
from requests.adapters import HTTPAdapter
import sys
import threading
import queue


HTTP_TIMEOUT = 3600  # (seconds)
NODE_CUSTOM_PORT = '12000'
LOCALHOST = "127.0.0.1"
UPDATE_INTERVAL = 5

from werkzeug.serving import WSGIRequestHandler

WSGIRequestHandler.protocol_version = "HTTP/1.1"
app = Flask(__name__)
api = Api(app)

msg_queue = {}



class ItemStore(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.items = []

    def add(self, item):
        with self.lock:
            self.items.append(item)

    def getAll(self):
        with self.lock:
            items, self.items = self.items, []
        return items


@app.route('/', methods=['POST'])
def handler():
    request_json_list = request.get_json()
    for request_json in request_json_list:
        print("Handle:")
        print(request_json)
    return 'OK'


def generate_url(ip=LOCALHOST, port=NODE_CUSTOM_PORT):
    return "http://" + ip + ":" + port


def send_msg():
    for destination_ip in msg_queue.keys():
        list_of_json_to_send = msg_queue[destination_ip].getAll()
        print("send msg to {} - nb_of_msgs: {} - json: {}".format(destination_ip, len(list_of_json_to_send), list_of_json_to_send))
        if len(list_of_json_to_send) > 0:
            my_session.post(generate_url(destination), json=list_of_json_to_send, timeout=HTTP_TIMEOUT)
    threading.Timer(5, send_msg).start()


def put_msg_in_queue(destination_ip, json_to_send):
    if destination_ip not in msg_queue:
        msg_queue[destination_ip] = ItemStore()
    msg_queue[destination_ip].add(json_to_send)
    print("Put msg {} in Queue of {}".format(json_to_send, destination))
    print("State of the queue of {} : {}".format(destination, msg_queue[destination_ip]))


if __name__ == '__main__':
    if sys.argv[1] == "receiver":
        my_session = requests.Session()
        from requests.adapters import HTTPAdapter
        my_session.mount('http://', HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=100))
        #send_msg()
        app.run(port=12000, host='0.0.0.0')

    elif sys.argv[1] == "sender":
        destination = sys.argv[2]
        my_session = requests.Session()
        from requests.adapters import HTTPAdapter

        send_msg()
        my_session.mount('http://', HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=100))

        for i in range(0,sys.argv[3]):
            send = {'type': 'DELETE', 'file_hash': 2135, 'file_src_ip': '10.16.8.31', 'remove_src_ip': '10.16.8.24',
             'remove_src_clock': 2, 'sender_ip': '10.16.8.26', 'sender_entry_ip': '10.16.8.31', 'sender_entry_clock': 0,
             'job_id': 228}

            put_msg_in_queue(generate_url(destination), send)

        print("end")
