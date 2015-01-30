import time
import collections
from pprint import pprint

import requests


def parse_yota_info(s):

    data = {}
    for line in filter(len, str.split(s, "\n")):

        k, v = str.split(line, "=")
        prev, curr = None, data
        for node in str.split(k, "."):

            if node not in curr:

                curr[node] = {}

            prev, curr = curr, curr[node]

        else:

            prev[node] = v

    return data


def speed_to_human(s):

    v = int(s)
    if v < 2 ** 20:

        s = str.format("{:.2f} Кбит/с", v / 2 ** 10)

    else:

        s = str.format("{:.2f} Мбит/с", v / 2 ** 20)

    return s


def speed_generator():

    while True:

        r = requests.get("http://10.0.0.1/status")
        d = parse_yota_info(r.text)
        yield tuple(map(int, (d["CurDownlinkThroughput"], d["CurUplinkThroughput"])))
        time.sleep(1)


size = 60
history = collections.deque(maxlen=size)
speed_down = False
for down, up in speed_generator():

    print(down, up)
    history.append(down)
    if len(history) == size:

        speed_low = all(map(lambda s: s < 320 * 0.9 * 2 ** 10, history))
        if speed_low and not speed_down:

            speed_down = True
            print("Speed down")

        elif not speed_low and speed_down:

            speed_down = False
            print("Speed up")


'''
while True:

    r = requests.get("http://10.0.0.1/status")
    d = parse_yota_info(r.text)
    print("↑" + speed_to_human(d["CurDownlinkThroughput"]), "↓" + speed_to_human(d["CurUplinkThroughput"]))
    time.sleep(1)
'''
