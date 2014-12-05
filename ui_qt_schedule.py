import datetime

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from bs4 import BeautifulSoup as bs


class YotaChangeSpeedEvent:

    short_days_of_week = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

    def __init__(self, event_time=None, speed=None, days_of_week=()):

        self.event_time = event_time or datetime.time()
        self.days_of_week = days_of_week
        self.speed = speed


    def __repr__(self):

        return str.format(
            "{} {} ({})",
            self.event_time.strftime("%H:%M"),
            self.speed,
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


class ScheduleUI(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()
        uic.loadUi("schedule.ui", self)
        self.schedule_model = ScheduleModel()
        self.slider_data = {'96604217': {'isSlot': False, 'optionInfo': {}, 'status': 'custom', 'autoprolongFlag': True, 'productId': 96604217, 'offerCode': 'POS-MA6-0013', 'isDeviceInUse': True, 'steps': [{'description': '{ "speed": "скорость до 64 Кбит/сек", "amount": "на 2 часа за 50 р. или на 24 часа за 150 р." }', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '365', 'remainString': 'дней', 'position': '0.0', 'theShortestOffer': False, 'speedNumber': '64', 'name': 'Бесплатный доступ на скорости до 64 Кбит/сек', 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Кбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0001', 'isDefaultSelectedPoint': False, 'payInfo': 'При подключении на ваш счет вернется 43.17  руб.', 'popup': None, 'isSweetPoint': False, 'swapAction': '0', 'isSpeedMaximum': False, 'isDisablingAutoprolong': True, 'amountNumber': '0', 'returnAmount': '43.17', 'isLight': True, 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '4', 'amountNumber': '300', 'remainString': 'дня', 'position': '0.05384615384615384', 'theShortestOffer': False, 'speedNumber': '320', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Кбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0002', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 320 Кбит/сек за 300 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '3', 'amountNumber': '350', 'remainString': 'дня', 'position': '0.10769230769230768', 'theShortestOffer': False, 'speedNumber': '416', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Кбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0003', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 416 Кбит/сек за 350 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '3', 'amountNumber': '400', 'remainString': 'дня', 'position': '0.16153846153846152', 'theShortestOffer': False, 'speedNumber': '512', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Кбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0004', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 512 Кбит/сек за 400 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '69', 'amountNumber': '450', 'remainString': 'часов', 'position': '0.21538461538461537', 'theShortestOffer': False, 'speedNumber': '640', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Кбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0005', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 640 Кбит/сек за 450 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '62', 'amountNumber': '500', 'remainString': 'часа', 'position': '0.2692307692307692', 'theShortestOffer': False, 'speedNumber': '768', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Кбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0006', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 768 Кбит/сек за 500 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '56', 'amountNumber': '550', 'remainString': 'часов', 'position': '0.32307692307692304', 'theShortestOffer': False, 'speedNumber': '896', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Кбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0007', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 896 Кбит/сек за 550 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '51', 'amountNumber': '600', 'remainString': 'час', 'position': '0.37692307692307686', 'theShortestOffer': False, 'speedNumber': '1.0', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0008', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 1 Мбит/сек за 600 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '47', 'amountNumber': '650', 'remainString': 'часов', 'position': '0.4307692307692307', 'theShortestOffer': False, 'speedNumber': '1.3', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0009', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 1,3 Мбит/сек за 650 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '44', 'amountNumber': '700', 'remainString': 'часа', 'position': '0.4846153846153845', 'theShortestOffer': False, 'speedNumber': '1.7', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0010', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 1,7 Мбит/сек за 700 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '41', 'amountNumber': '750', 'remainString': 'час', 'position': '0.5384615384615383', 'theShortestOffer': False, 'speedNumber': '2.1', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0011', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 2,1 Мбит/сек за 750 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '38', 'amountNumber': '800', 'remainString': 'часов', 'position': '0.5923076923076922', 'theShortestOffer': False, 'speedNumber': '3.1', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0012', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 3,1 Мбит/сек за 800 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '36', 'speedString': 'Мбит/сек (макс.)', 'remainString': 'часов', 'position': '0.6461538461538461', 'theShortestOffer': False, 'speedNumber': '4.1', 'name': '30 дней на скорости до 4,1 Мбит/сек за 850 руб.', 'isLight': False, 'moneyEnough': True, 'offerDisabled': True, 'isSpecialOffer': False, 'payFromCard': '0', 'code': 'POS-MA6-0013', 'isDefaultSelectedPoint': True, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'swapAction': '0', 'isSpeedMaximum': False, 'amountNumber': '850', 'returnAmount': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '34', 'amountNumber': '900', 'remainString': 'часа', 'position': '0.7', 'theShortestOffer': False, 'speedNumber': '5.0', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0014', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': True, 'returnAmount': '0', 'name': '30 дней на скорости до 5 Мбит/сек за 900 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '32', 'amountNumber': '950', 'remainString': 'часа', 'position': '0.73', 'theShortestOffer': False, 'speedNumber': '5.7', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0015', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 5,7 Мбит/сек за 950 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '31', 'amountNumber': '1000', 'remainString': 'час', 'position': '0.76', 'theShortestOffer': False, 'speedNumber': '6.4', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0016', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 6,4 Мбит/сек за 1000 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '29', 'amountNumber': '1050', 'remainString': 'часов', 'position': '0.79', 'theShortestOffer': False, 'speedNumber': '7.1', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0017', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 7,1 Мбит/сек за 1050 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '28', 'amountNumber': '1100', 'remainString': 'часов', 'position': '0.8200000000000001', 'theShortestOffer': False, 'speedNumber': '7.8', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0018', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 7,8 Мбит/сек за 1100 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '27', 'amountNumber': '1150', 'remainString': 'часов', 'position': '0.8500000000000001', 'theShortestOffer': False, 'speedNumber': '8.5', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0019', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 8,5 Мбит/сек за 1150 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '25', 'amountNumber': '1200', 'remainString': 'часов', 'position': '0.8800000000000001', 'theShortestOffer': False, 'speedNumber': '9.2', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0020', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 9,2 Мбит/сек за 1200 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '24', 'amountNumber': '1250', 'remainString': 'часа', 'position': '0.9100000000000001', 'theShortestOffer': False, 'speedNumber': '10.0', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0021', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 10 Мбит/сек за 1250 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '23', 'amountNumber': '1300', 'remainString': 'часа', 'position': '0.9400000000000002', 'theShortestOffer': False, 'speedNumber': '12.0', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0022', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 12 Мбит/сек за 1300 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '&nbsp;', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '23', 'amountNumber': '1350', 'remainString': 'часа', 'position': '0.9700000000000002', 'theShortestOffer': False, 'speedNumber': '15.0', 'isSpeedMaximum': False, 'isSpecialOffer': False, 'moneyEnough': True, 'speedString': 'Мбит/сек (макс.)', 'payFromCard': '0', 'code': 'POS-MA6-0023', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на скорости до 15 Мбит/сек за 1350 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}, {'description': '30 дней без ограничения скорости 1400 руб. в месяц', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '22', 'amountNumber': '1400', 'remainString': 'часа', 'position': '1.0', 'theShortestOffer': True, 'speedNumber': '<div class="max-value">Макс.</div>', 'isSpeedMaximum': True, 'isSpecialOffer': True, 'moneyEnough': True, 'speedString': 'Мбит/сек', 'payFromCard': '0', 'code': 'POS-MA6-0024', 'isDefaultSelectedPoint': False, 'payInfo': '', 'popup': None, 'isSweetPoint': False, 'returnAmount': '0', 'name': '30 дней на максимальной скорости за 1400 руб.', 'isLight': False, 'swapAction': '0', 'payFromBalance': '0'}], 'specialOffers': [{'description': '5400 р. за полгода, то есть 900 р. в месяц', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '183', 'amountNumber': '5400', 'remainString': 'дня', 'position': 'null', 'theShortestOffer': False, 'speedNumber': '<div class="max-value">Макс.</div>', 'isSpeedMaximum': True, 'isSpecialOffer': True, 'moneyEnough': False, 'speedString': 'Мбит/сек', 'payFromCard': '5307.83', 'code': 'POS-MA6-0025', 'isDefaultSelectedPoint': False, 'payInfo': 'При подключении со счета будет списано 5356.83  руб.', 'popup': 'При подключении на срок более одного месяца предоставляется скидка за предоплаченный период.<br/><br/>В дальнейшем сокращение срока подключения возможно только с пересчетом использованного периода по более высокой цене, без учета предоставляемой скидки.', 'isSweetPoint': False, 'returnAmount': '0', 'name': '6 месяцев на максимальной скорости', 'isLight': False, 'swapAction': '0', 'payFromBalance': '50'}, {'description': '9000 р. за год, то есть 750 р. в месяц', 'amountString': 'руб. в месяц', 'swapCondition': '0', 'remainNumber': '366', 'amountNumber': '9000', 'remainString': 'дней', 'position': 'null', 'theShortestOffer': False, 'speedNumber': '<div class="max-value">Макс.</div>', 'isSpeedMaximum': True, 'isSpecialOffer': True, 'moneyEnough': False, 'speedString': 'Мбит/сек', 'payFromCard': '8907.83', 'code': 'POS-MA6-0026', 'isDefaultSelectedPoint': False, 'payInfo': 'При подключении со счета будет списано 8956.83  руб.', 'popup': 'При подключении на срок более одного месяца предоставляется скидка за предоплаченный период.<br/><br/>В дальнейшем сокращение срока подключения возможно только с пересчетом использованного периода по более высокой цене, без учета предоставляемой скидки.', 'isSweetPoint': False, 'returnAmount': '0', 'name': '12 месяцев на максимальной скорости', 'isLight': False, 'swapAction': '0', 'payFromBalance': '50'}], 'sliderEnabled': True, 'connectEnabled': True, 'connectVisible': True, 'currentProduct': {'description': '&nbsp;', 'offerDisabled': True, 'isSpecialOffer': False, 'isSweetPoint': False, 'isDefaultSelectedPoint': False, 'speedString': 'Мбит/сек (макс.)', 'amountNumber': '850', 'code': 'POS-MA6-0013', 'position': '0.0', 'theShortestOffer': False, 'name': '30 дней на скорости до 4,1 Мбит/сек за 850 руб.', 'isLight': False, 'speedNumber': '4.1', 'isSpeedMaximum': False, 'amountString': 'руб. в месяц'}, 'isHomeRegion': True, 'isTestDrive': False, 'optionList': []}}

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
        print(ed.result())


    def ui_close_event(self, e):

        e.ignore()
        self.hide()


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

        for prefix inf EditSchedule.days_of_week:

            box = getattr(self, prefix + "_checkbox")
            if box.checkState() == QtCore.Qt.Checked:

                pass



if __name__ == "__main__":

    import sys
    app = QtWidgets.QApplication(sys.argv)
    y = ScheduleUI()
    y.show()
    sys.exit(app.exec_())
