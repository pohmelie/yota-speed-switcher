#!/usr/bin/python3

import re
import json
import sys
import queue

import requests
from bs4 import BeautifulSoup as bs
from PyQt5 import QtCore, QtGui, QtWidgets, uic


def yota(username, password, speed=None):

    s = requests.Session()

    v = re.sub(r"(\D)", "", username)
    token = username
    s.get("https://my.yota.ru")
    if "@" in username:

        r = s.post("https://my.yota.ru/selfcare/login/getUidByMail", data={"value": username})
        status, user_id = str.split(r.text, "|")
        if status == "ok":

            token = user_id

    elif len(v) > 10:

        r = s.post(
            "https://my.yota.ru/selfcare/login/getUidByPhone",
            data={
                "value": v,
            }
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
        }
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
    )

    return yota(username, password)


class YotaWorker(QtCore.QObject):

    result = QtCore.pyqtSignal(dict)

    def __init__(self):

        super().__init__()
        self._request_queue = queue.Queue()

        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)
        self.thread.start()


    def request(self, *args):

        self._request_queue.put_nowait(args)


    @QtCore.pyqtSlot()
    def run(self):

        while True:

            self.result.emit(yota(*self._request_queue.get()))


class YotaUI:

    def __init__(self):

        self.ui = uic.loadUi("login.ui")
        self.ui.login_button.clicked.connect(self.login)
        self.ui.username_edit.returnPressed.connect(self.login)
        self.ui.password_edit.returnPressed.connect(self.login)
        self.ui.setWindowIcon(QtGui.QIcon("logo-yota.png"))
        self.ui.setWindowTitle("yota-speed-switcher")
        self.ui.show()


    def login(self):

        self.menu = QtWidgets.QMenu()
        self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon("logo-yota-gray.png"))
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.menu.exec)
        self.tray.show()
        if sys.platform == "linux":

            mbox = QtWidgets.QMessageBox()
            mbox.setText("Do you see tray icon?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

            while mbox.exec() == QtWidgets.QMessageBox.No:

                self.tray.hide()
                self.tray.show()

        self.ui.setEnabled(False)
        self.username = self.ui.username_edit.text()
        self.password = self.ui.password_edit.text()

        self.worker = YotaWorker()
        self.worker.result.connect(self.refresh_menu)
        self.worker.request(self.username, self.password)


    QtCore.pyqtSlot(dict)
    def refresh_menu(self, slider_data):

        self.ui.hide()
        self.ui.setEnabled(True)
        self.tray.setIcon(QtGui.QIcon("logo-yota.png"))

        data = next(iter(slider_data.values()))
        self.menu.clear()
        fields = (
            "speedNumber",
            "speedString",
            "remainNumber",
            "remainString",
            "amountNumber",
            "amountString",
        )
        fmt = "{} {} ({} {}, {} {})"
        self.steps = {}
        self.actions = []
        for step in data["steps"]:

            desc = str.format(fmt, *map(lambda k: bs(step[k]).text, fields))
            self.steps[fmt] = step["code"]
            action = QtWidgets.QAction(desc, self.ui)
            action.setCheckable(True)
            if step["code"] == data["offerCode"]:

                action.setChecked(True)
                self.menu.setToolTip(desc)

            self.menu.addAction(action)
            action.triggered.connect(self.SpeedSetter(step["code"], action))
            self.actions.append(action)

        self.menu.addSeparator()
        action = self.menu.addAction("Обновить…")
        action.triggered.connect(self.SpeedSetter())
        self.actions.append(action)
        self.menu.addAction("Выход").triggered.connect(sys.exit)


    def SpeedSetter(self, code=None, action=None):

        def speed_setter():

            self.worker.request(self.username, self.password, code)
            self.tray.setIcon(QtGui.QIcon("logo-yota-gray.png"))
            if action is not None:

                action.setChecked(False)

            for a in self.actions:

                a.setEnabled(False)

        return speed_setter


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    y = YotaUI()
    sys.exit(app.exec_())
