#!/usr/bin/python3
'''yota speed switcher

Usage:
    yota-speed-switcher [pyqt5 | urwid]
'''
import collections


def try_pyqt5():

    import sys
    from PyQt5 import QtWidgets
    from ui_qt import YotaUI
    app = QtWidgets.QApplication(sys.argv)
    y = YotaUI()
    sys.exit(app.exec_())


def try_urwid():

    import urwid
    from ui_urwid import YotaUI

    ui = YotaUI()
    loop = urwid.MainLoop(ui.ui)
    ui.set_loop(loop)
    loop.run()


scheme = collections.OrderedDict((
    ("pyqt5", try_pyqt5),
    ("urwid", try_urwid),
))


if __name__ == "__main__":

    import os

    os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.getcwd(), "cacert.pem")

    from docopt import docopt

    args = docopt(__doc__, version="yota speed switcher")
    if any(args.values()):

        for t, value in args.items():

            if value:

                scheme[t]()
                break

    else:

        for f in scheme.values():

            try:

                f()
                break

            except ImportError:

                print(str.format("'{}' import failed", f.__name__))
