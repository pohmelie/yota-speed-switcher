#!/usr/bin/python3
'''yota speed switcher

Usage:
    yota-speed-switcher [pyqt5 | urwid]
'''

def try_pyqt5():

    import sys
    from PyQt5 import QtWidgets
    from ui_qt import YotaUI
    app = QtWidgets.QApplication(sys.argv)
    y = YotaUI()
    sys.exit(app.exec_())


def try_urwid():

    import urwid


scheme = (
    ("pyqt5", try_pyqt5),
    ("urwid", try_urwid),
)


if __name__ == "__main__":

    from docopt import docopt

    args = docopt(__doc__, version="yota speed switcher")
    if any(args.values()):

        for t, value in args.items():

            if value:

                scheme[t]()
                break

    else:

        for _, f in scheme:

            try:

                f()
                break

            except ImportError:

                print(str.format("'{}' import failed", f.__name__))
