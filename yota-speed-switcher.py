#!/usr/bin/python3

def try_pyqt5():

    import foobar
    import sys
    from PyQt5 import QtWidgets
    from ui_qt import YotaUI
    app = QtWidgets.QApplication(sys.argv)
    y = YotaUI()
    sys.exit(app.exec_())


def try_urwid():

    import urwid


if __name__ == "__main__":

    for f in (try_pyqt5, try_urwid):

        try:

            f()
            break

        except ImportError:

            print(str.format("'{}' import failed", f.__name__))
