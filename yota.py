import re
import json

import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs


class YotaBadMail(Exception): pass
class YotaBadPhoneNumber(Exception): pass


class YotaSpeed:

    def __init__(self, step):

        self.code = step["code"]
        self.amount = str.format("{} {}", step["amountNumber"], step["amountString"])
        self.remain = str.format("{} {}", step["remainNumber"], step["remainString"])
        self.speed = str.format("{} {}", bs(step["speedNumber"]).text, step["speedString"])
        self.bps = YotaSpeed.parse_speed(self.speed)


    @staticmethod
    def parse_speed(s):

        try:

            v, speed, *_ = str.split(s)
            if "Кбит" in speed:

                mul = 2 ** 10

            else:

                mul = 2 ** 20

            return int(float(v) * mul)

        except ValueError:

            return None


    def __repr__(self):

        return str.format("{} ({}, {})", self.speed, self.remain, self.amount)


class YotaSlider:

    def __init__(self, slider):

        self._raw = slider
        self.steps = tuple(map(YotaSpeed, self._raw["steps"]))
        self.selected = None
        for i, step in enumerate(self.steps):

            if step.code == slider["offerCode"]:

                self.selected = i


@asyncio.coroutine
def yota(username, password, speed=None, timeout=10):

    c = aiohttp.TCPConnector(share_cookies=True)
    v = re.sub(r"(\D)", "", username)
    token = username

    yield from asyncio.wait_for(
        aiohttp.request(
            "get",
            "https://my.yota.ru",
            connector=c,
        ),
        timeout,
    )

    if "@" in username:

        r = yield from asyncio.wait_for(
            aiohttp.request(
                "post",
                "https://my.yota.ru/selfcare/login/getUidByMail",
                data={"value": username},
                connector=c,
            ),
            timeout,
        )

        status, user_id = str.split((yield from r.text()), "|")
        if status != "ok":

            raise YotaBadMail(str.format("'{}'", username))

        token = user_id

    elif len(v) > 10:

        r = yield from asyncio.wait_for(
            aiohttp.request(
                "post",
                "https://my.yota.ru/selfcare/login/getUidByPhone",
                data={"value": v},
                connector=c,
            ),
            timeout,
        )

        status, user_id = str.split((yield from r.text()), "|")
        if status != "ok":

            raise YotaBadPhoneNumber(str.format("'{}'", v))

        token = user_id

    r = yield from asyncio.wait_for(
        aiohttp.request(
            "post",
            "https://login.yota.ru/UI/Login",
            params={
                "goto": "https://my.yota.ru:443/selfcare/loginSuccess",
                "gotoOnFail": "https://my.yota.ru:443/selfcare/loginError",
                "org": "customer",
                "IDToken2": password,
                "IDToken1": token,
            },
            connector=c,
        ),
        timeout,
    )

    txt = yield from r.text()
    for line in map(str.strip, str.split(txt, "\n")):

        if str.startswith(line, "var sliderData = "):

            slider_data = json.loads(str.replace(line, "var sliderData = ", "")[:-1])
            break

    if speed is None:

        return slider_data

    phtml = bs(txt)
    form = phtml.find("form")
    parameters = {}
    for inp in form("input"):

        if inp.has_attr("name") and inp.has_attr("value"):

            parameters[inp["name"]] = inp["value"]
            print(inp["name"], inp["value"])

    parameters["offerCode"] = speed

    yield from asyncio.wait_for(
        aiohttp.request(
            "post",
            "https://my.yota.ru/selfcare/devices/changeOffer",
            params=parameters,
            connector=c,
        ),
        timeout,
    )

    return (yield from yota(username, password))
