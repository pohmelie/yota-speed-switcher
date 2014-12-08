import sys
import queue
import json
import pathlib
import functools
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from bs4 import BeautifulSoup as bs

from ui_qt_schedule import ScheduleUI
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

                self.result.emit(yota(*self._request_queue.get()))

            except:

                self.result.emit({})


class YotaUI:

    def __init__(self):

        self.login_ui = uic.loadUi("login.ui")
        self.login_ui.login_button.clicked.connect(self.login)
        self.login_ui.username_edit.returnPressed.connect(self.login)
        self.login_ui.password_edit.returnPressed.connect(self.login)
        self.login_ui.setWindowIcon(QtGui.QIcon("logo-yota.png"))
        self.login_ui.setWindowTitle("yota-speed-switcher")
        self.hide_on_close(self.login_ui)

        self.schedule_ui = ScheduleUI()
        self.schedule_ui.schedules_refreshed.connect(self.schedules_refreshed)
        self.hide_on_close(self.schedule_ui)

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

        self.launched = {}
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_schedule)
        self.timer.start(1000)


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
    def schedules_refreshed(self, schedules):

        self.options["schedule_data"] = schedules
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
                    "schedules": [],
                    "use_schedules": False,
                },
            }


    def set_options(self):

        self.login_ui.username_edit.setText(self.options["username"])
        self.login_ui.password_edit.setText(self.options["password"])
        self.login_ui.remember_me_edit.setCheckState(QtCore.Qt.Checked if self.options["remember_me"] else QtCore.Qt.Unchecked)
        self.schedule_ui.load_schedules(self.options["schedule_data"])


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
        self.worker.result.connect(self.schedule_ui.set_slider_data)
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
            self.steps = {}
            self.actions = []
            for step in data["steps"]:

                desc = str.format(fmt, *map(lambda k: bs(step[k]).text, fields))
                self.steps[fmt] = step["code"]
                action = QtWidgets.QAction(desc, self.login_ui)
                action.setCheckable(True)
                print(step["code"], step["speedNumber"], step["speedString"])
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

        self.menu.addAction("Расписание...").triggered.connect(lambda: self.schedule_ui.show())
        self.menu.addAction("Смена пользователя").triggered.connect(self.logout)
        self.menu.addAction("Выход").triggered.connect(sys.exit)


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

            self.worker.request(self.options["username"], self.options["password"], code)
            self.tray.setIcon(QtGui.QIcon("logo-yota-gray.png"))
            if action is not None:

                action.setChecked(False)

            for a in self.actions:

                a.setEnabled(False)

        return speed_setter
