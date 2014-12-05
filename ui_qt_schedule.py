import datetime

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from bs4 import BeautifulSoup as bs


class YotaChangeSpeedEvent:

    short_days_of_week = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

    def __init__(self, event_time=None, speed=None, days_of_week=()):

        self.event_time = event_time or datetime.time()
        self.days_of_week = days_of_week
        self.speed = speed


    def to_dict(self):

        return {
            "event_time": (self.event_time.hour, self.event_time.minute),
            "days_of_week": self.days_of_week,
            "speed": self.speed,
        }


    @staticmethod
    def from_dict(d):

        return YotaChangeSpeedEvent(
            datetime.time(*d["event_time"]),
            d["speed"],
            d["days_of_week"],
        )


    def __repr__(self):

        return str.format(
            "{} [{}] ({})",
            self.event_time.strftime("%H:%M"),
            self.speed or "-",
            str.join(", ", map(YotaChangeSpeedEvent.short_days_of_week.__getitem__, self.days_of_week)),
        )


class ScheduleModel(QtCore.QAbstractListModel):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.schedules = []


    def append(self, e):

        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.schedules.append(e)
        self.endInsertRows()


    def remove(self, row):

        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self.schedules.pop(row)
        self.endRemoveRows()


    def rowCount(self, parent=None):

        return len(self.schedules)


    def data(self, index, role):

        if role == QtCore.Qt.DisplayRole:

            return repr(self.schedules[index.row()])


    def clear(self):

        self.reset()
        self.schedules = []


class ScheduleUI(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()
        uic.loadUi("schedule.ui", self)
        self.schedule_model = ScheduleModel()

        self.schedule_view.setModel(self.schedule_model)
        self.schedule_view.doubleClicked.connect(self.edit)
        self.add_schedule_button.clicked.connect(self.add_schedule)
        self.remove_schedule_button.clicked.connect(self.remove_schedule)

        self.setWindowIcon(QtGui.QIcon("logo-yota.png"))
        self.setWindowTitle("Расписание")


    QtCore.pyqtSlot(dict)
    def set_slider_data(self, slider_data):

        print(slider_data)
        self.slider_data = slider_data


    def add_schedule(self):

        self.schedule_model.append(YotaChangeSpeedEvent())


    def remove_schedule(self):

        self.schedule_model.remove(self.schedule_view.currentIndex().row())


    def edit(self, index):

        ed = EditSchedule(self.slider_data, self)
        ed.set_event(self.schedule_model.schedules[index.row()])
        ed.setWindowTitle("Редактирование события")
        ed.exec()
        if ed.result():

            self.schedule_model.schedules[index.row()] = ed.get_event()
            self.schedule_model.dataChanged.emit(index, index)


    def ui_close_event(self, e):

        e.ignore()
        self.hide()


    def dump_schedules(self):

        return tuple(map(operator.methodcaller("to_dict"), self.schedule_model.schedules))


    def load_schedules(self, o):

        self.schedule_model.reset()
        for d in o:

            self.schedule_model.append(YotaChangeSpeedEvent.from_dict(d))


class EditSchedule(QtWidgets.QDialog):

    days_of_week = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

    def __init__(self, speed_info, parent=None):

        super().__init__(parent)
        uic.loadUi("edit_dialog.ui", self)

        self.accept_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.speed_texts = []
        if speed_info is not None:

            data = next(iter(speed_info.values()))
            for step in data["steps"]:

                s = str.format("{} {}", bs(step["speedNumber"]).text, step["speedString"])
                self.speed_chooser.addItem(s)
                self.speed_texts.append(s)


    def set_event(self, e):

        for day in e.days_of_week:

            box = getattr(self, EditSchedule.days_of_week[day] + "_checkbox")
            box.setCheckState(QtCore.Qt.Checked)

        self.time_edit.setTime(e.event_time)
        if e.speed not in self.speed_texts:

            self.speed_chooser.setCurrentIndex(-1)

        else:

            self.speed_chooser.setCurrentIndex(self.speed_texts.index(e.speed))


    def get_event(self):

        days = []
        for i, prefix in enumerate(EditSchedule.days_of_week):

            box = getattr(self, prefix + "_checkbox")
            if box.checkState() == QtCore.Qt.Checked:

                days.append(i)

        if self.speed_chooser.currentIndex() != -1:

            speed = self.speed_texts[self.speed_chooser.currentIndex()]

        else:

            speed = None

        event_time = self.time_edit.time().toPyTime()
        return YotaChangeSpeedEvent(event_time, speed, days)


if __name__ == "__main__":

    import sys
    app = QtWidgets.QApplication(sys.argv)
    y = ScheduleUI()
    y.show()
    sys.exit(app.exec_())
