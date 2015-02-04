import re
import json

import requests
from bs4 import BeautifulSoup as bs


def yota(username, password, speed=None, timeout=4):

    s = requests.Session()

    v = re.sub(r"(\D)", "", username)
    token = username
    s.get("https://my.yota.ru")
    if "@" in username:

        r = s.post(
            "https://my.yota.ru/selfcare/login/getUidByMail",
            data={"value": username},
            timeout=timeout,
        )
        status, user_id = str.split(r.text, "|")
        if status == "ok":

            token = user_id

    elif len(v) > 10:

        r = s.post(
            "https://my.yota.ru/selfcare/login/getUidByPhone",
            data={
                "value": v,
            },
            timeout=timeout,
        )
        status, user_id = str.split(r.text, "|")
        if status == "ok":

            token = user_id

    r = s.post(
        "https://login.yota.ru/UI/Login",
        params={
            "goto": "https://my.yota.ru:443/selfcare/loginSuccess",
            "gotoOnFail": "https://my.yota.ru:443/selfcare/loginError",
            "org": "customer",
            "IDToken2": password,
            "IDToken1": token,
        },
        timeout=timeout,
    )

    for line in map(str.strip, str.split(r.text, "\n")):

        if str.startswith(line, "var sliderData = "):

            slider_data = json.loads(str.replace(line, "var sliderData = ", "")[:-1])
            break

    if speed is None:

        return slider_data

    phtml = bs(r.text)
    form = phtml.find("form")
    parameters = {
        "isDisablingAutoprolong": "false",
    }
    for inp in form("input"):

        if inp.has_attr("name") and inp.has_attr("value"):

            parameters[inp["name"]] = inp["value"]

    parameters["offerCode"] = speed
    r = s.post(
        "https://my.yota.ru/selfcare/devices/changeOffer",
        params=parameters,
        timeout=timeout,
    )

    return yota(username, password)
