import sys
import queue
import json
import pathlib
import functools
import datetime
import time
import collections
import textwrap

import requests
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from bs4 import BeautifulSoup as bs

from ui_qt_options import OptionsUI
from yota import yota


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

            try:

                args = self._request_queue.get()
                while True:

                    try:

                        self.result.emit(yota(*args))
                        break

                    except:

                        time.sleep(5)
                        continue

            except:

                self.result.emit({})


class StatusWorker(QtCore.QObject):

    result = QtCore.pyqtSignal(dict)

    def __init__(self):

        super().__init__()

        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)
        self.thread.start()


    def parse_yota_info(self, s):

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


    @QtCore.pyqtSlot()
    def run(self):

        while True:

            try:

                start = datetime.datetime.now()
                r = requests.get("http://10.0.0.1/status", timeout=1)
                d = self.parse_yota_info(r.text)
                self.result.emit(d)

            except:

                pass

            end = datetime.datetime.now()
            time.sleep(max(0, 1 - (end - start).total_seconds()))


class YotaUI:

    def __init__(self):

        self.login_ui = uic.loadUi("login.ui")
        self.login_ui.login_button.clicked.connect(self.login)
        self.login_ui.username_edit.returnPressed.connect(self.login)
        self.login_ui.password_edit.returnPressed.connect(self.login)
        self.login_ui.setWindowIcon(QtGui.QIcon("logo-yota.png"))
        self.login_ui.setWindowTitle("yota-speed-switcher")
        self.hide_on_close(self.login_ui)

        self.options_ui = OptionsUI()
        self.options_ui.options_refreshed.connect(self.options_refreshed)
        self.hide_on_close(self.options_ui)

        self.options_filename = "options.json"
        self.load_options()
        self.set_options()

        self.menu = QtWidgets.QMenu()
        self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon("logo-yota-gray.png"))
        self.tray.setContextMenu(self.menu)
        self.tray.show()
        if sys.platform == "linux":

            mbox = QtWidgets.QMessageBox()
            mbox.setText("Do you see tray icon?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

            while mbox.exec() == QtWidgets.QMessageBox.No:

                self.tray.hide()
                self.tray.show()

        self.refresh_menu()
        if self.options["remember_me"]:

            self.login_ui.setEnabled(False)
            self.login()

        self.login_ui.show()

        self.actions = None
        self.switching_speed = False
        self.speed_memory = []
        self.speed_start_time = datetime.datetime.now()
        self.speed_status_worker = StatusWorker()
        self.speed_status_worker.result.connect(self.speed_status_refresh)

        self.launched = {}
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_schedule)
        self.timer.start(1000)


    @staticmethod
    def human_speed(x):

        x = int(x)
        if x < 2 ** 20:

            s = "{:.2f} Kibit/s".format(x / 2 ** 10)

        else:

            s = "{:.2f} Mibit/s".format(x / 2 ** 20)

        return s


    @staticmethod
    def human_size(x):

        x = int(x)
        suffixes = ("B", "KiB", "MiB", "GiB", "TiB")
        for i, name in enumerate(suffixes):

            div = 2 ** (10 * i)
            if x / div < 2 ** 10 or i == len(suffixes) - 1:

                if div == 1:

                    s = "{} {}".format(x, name)

                else:

                    s = "{:.2f} {}".format(x / div, name)

                break

        return s


    @staticmethod
    def parse_speed(s):

        v, speed, *_ = s.split()
        try:

            if "Кбит" in speed:

                mul = 2 ** 10

            else:

                mul = 2 ** 20

            return int(float(v) * mul)

        except:

            pass


    @QtCore.pyqtSlot(dict)
    def speed_status_refresh(self, d):

        if "ConnectedTime" not in d:

            return

        template = textwrap.dedent('''\
            {connected_time}
            {max_down} / {max_up}
            {curr_down} / {curr_up}
            {data_recv} / {data_send}
            {SINR} dB / {RSRP} dBm
            {ip}
            {firmware}
        ''').strip()
        self.options_ui.status_view.setText(template.format(
            connected_time=datetime.timedelta(seconds=int(d["ConnectedTime"])),
            max_down=YotaUI.human_speed(d["MaxDownlinkThroughput"]),
            max_up=YotaUI.human_speed(d["MaxUplinkThroughput"]),
            curr_down=YotaUI.human_speed(d["CurDownlinkThroughput"]),
            curr_up=YotaUI.human_speed(d["CurUplinkThroughput"]),
            data_recv=YotaUI.human_size(d["ReceivedBytes"]),
            data_send=YotaUI.human_size(d["SentBytes"]),
            SINR=d["3GPP"]["SINR"],
            RSRP=d["3GPP"]["RSRP"],
            ip=d["IP"],
            firmware=d["FirmwareVersion"],
        ))

        if not self.switching_speed:

            if self.actions and self.options["autospeed_data"]["use_autospeed"]:

                low_index = self.options["autospeed_data"]["low_speed_index"]
                high_index = self.options["autospeed_data"]["high_speed_index"]
                desc = self.actions[low_index].text()
                low_speed = YotaUI.parse_speed(desc)
                curr_speed =  max(map(int, (d["CurDownlinkThroughput"], d["CurUplinkThroughput"])))

                self.speed_memory.append(curr_speed)
                low_timeout = self.options["autospeed_data"]["low_speed_timeout"]
                high_timeout = self.options["autospeed_data"]["high_speed_timeout"]
                self.speed_memory = self.speed_memory[-max(low_timeout, high_timeout):]
                if low_speed is not None:

                    low_bound_speed = low_speed * self.options["autospeed_data"]["low_speed_threshold"] / 100
                    if (
                        len(self.speed_memory) >= high_timeout and
                        sum(self.speed_memory[-high_timeout:]) / high_timeout > low_bound_speed and
                        any(map(lambda i: self.actions[i].isChecked(), range(low_index + 1)))
                    ):

                        self.actions[high_index].triggered.emit()

                    elif (
                        len(self.speed_memory) >= low_timeout and
                        max(self.speed_memory[-low_timeout:]) <= low_bound_speed and
                        any(map(lambda i: self.actions[i].isChecked(), range(low_index + 1, len(self.actions))))
                    ):

                        self.actions[low_index].triggered.emit()


    def check_schedule(self):

        if not self.options["schedule_data"]["use_schedules"]:

            return

        dt = datetime.datetime.today()
        d = datetime.date.today()
        for schedule in self.options["schedule_data"]["schedules"]:

            h, m = schedule["event_time"]
            label = (h, m, schedule["speed"])
            if label in self.launched and self.launched[label] == d:

                continue

            if dt.weekday() in schedule["days_of_week"] and dt.hour == h and dt.minute == m:

                self.launched[label] = d
                for action in self.actions:

                    if str.startswith(action.text(), schedule["speed"]):

                        action.triggered.emit()


    @QtCore.pyqtSlot(dict)
    def options_refreshed(self, o):

        self.options.update(o)
        self.save_options()


    def hide_on_close(self, ui):

        def ui_close_event(e):

            e.ignore()
            ui.hide()

        ui.closeEvent = ui_close_event


    def load_options(self):

        f = pathlib.Path(self.options_filename)
        try:

            self.options = json.load(f.open())

        except:

            if f.is_file():

                f.unlink()

            self.options = {
                "username": "",
                "password": "",
                "remember_me": False,
                "schedule_data": {
                    "use_schedules": False,
                    "schedules": [],
                },
                "autospeed_data": {
                    "use_autospeed": False,
                    "low_speed_index": 1,
                    "high_speed_index": 12,
                    "low_speed_timeout": 300,
                    "high_speed_timeout": 5,
                    "low_speed_threshold": 80,
                }
            }


    def set_options(self):

        self.login_ui.username_edit.setText(self.options["username"])
        self.login_ui.password_edit.setText(self.options["password"])
        self.login_ui.remember_me_edit.setCheckState(QtCore.Qt.Checked if self.options["remember_me"] else QtCore.Qt.Unchecked)
        self.options_ui.load_options(self.options)


    def save_options(self):

        f = pathlib.Path(self.options_filename)
        try:

            o = self.options.copy()
            if not o["remember_me"]:

                o["password"] = ""

            json.dump(o, f.open(mode="w"), indent=4)

        except:

            self.show_baloon("Can't save options")
            if f.is_file():

                f.unlink()


    def get_options(self):

        self.options["username"] = self.login_ui.username_edit.text()
        self.options["password"] = self.login_ui.password_edit.text()
        self.options["remember_me"] = self.login_ui.remember_me_edit.checkState() == QtCore.Qt.Checked


    def show_baloon(self, text):

        if QtWidgets.QSystemTrayIcon.supportsMessages():

            self.tray.showMessage("yota-speed-switcher", text)

        else:

            print(text)


    def login(self):

        self.login_ui.setEnabled(False)
        self.get_options()
        self.save_options()

        self.worker = YotaWorker()
        self.worker.result.connect(self.refresh_menu)
        self.worker.result.connect(self.options_ui.set_slider_data)
        self.worker.request(self.options["username"], self.options["password"])


    QtCore.pyqtSlot(dict)
    def refresh_menu(self, slider_data=None):

        self.menu.clear()
        self.login_ui.setEnabled(True)
        if isinstance(slider_data, dict) and not slider_data:

            self.show_baloon("Can't login")

        elif slider_data is not None:

            self.login_ui.hide()
            self.tray.setIcon(QtGui.QIcon("logo-yota.png"))

            data = next(iter(slider_data.values()))
            fields = (
                "speedNumber",
                "speedString",
                "remainNumber",
                "remainString",
                "amountNumber",
                "amountString",
            )
            fmt = "{} {} ({} {}, {} {})"
            self.actions = []
            for step in data["steps"]:

                desc = str.format(fmt, *map(lambda k: bs(step[k]).text, fields))
                action = QtWidgets.QAction(desc, self.login_ui)
                action.setCheckable(True)
                if step["code"] == data["offerCode"]:

                    action.setChecked(True)
                    self.menu.setToolTip(desc)
                    self.show_baloon(desc)

                self.menu.addAction(action)
                action.triggered.connect(self.SpeedSetter(step["code"], action))
                self.actions.append(action)

            self.menu.addSeparator()
            action = self.menu.addAction("Обновить")
            action.triggered.connect(self.SpeedSetter())
            self.actions.append(action)

        self.menu.addAction("Настройки...").triggered.connect(lambda: self.options_ui.show())
        self.menu.addAction("Смена пользователя").triggered.connect(self.logout)
        self.menu.addAction("Выход").triggered.connect(sys.exit)
        self.switching_speed = False


    def remove_options(self):

        try:

            f = pathlib.Path(self.options_filename)
            if f.is_file():

                f.unlink()

        except:

            self.show_baloon("Can't remove options file")

        self.options["remember_me"] = False
        self.set_options()


    def logout(self):

        self.remove_options()
        self.refresh_menu()
        self.tray.setIcon(QtGui.QIcon("logo-yota-gray.png"))
        self.login_ui.show()


    def SpeedSetter(self, code=None, action=None):

        def speed_setter():

            self.switching_speed = True
            self.worker.request(self.options["username"], self.options["password"], code)
            self.tray.setIcon(QtGui.QIcon("logo-yota-gray.png"))
            if action is not None:

                action.setChecked(False)

            for a in self.actions:

                a.setEnabled(False)

        return speed_setter
