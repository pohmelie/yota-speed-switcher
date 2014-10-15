import urwid

from bs4 import BeautifulSoup as bs

from yota import yota


class YotaUI:

    def __init__(self):

        self.username_edit = urwid.Edit(caption="username: ", wrap="clip")
        self.password_edit = urwid.Edit(caption="password: ", wrap="clip", mask="*")
        self.login_button = urwid.Button("Login", on_press=self.login_clicked)
        self.status = urwid.Text("")

        self.login_ui = urwid.Pile(
            (
                urwid.LineBox(self.username_edit),
                urwid.LineBox(self.password_edit),
                self.login_button,
            )
        )

        self.common_container = urwid.Filler(self.login_ui)
        self.ui = urwid.Frame(self.common_container, footer=self.status)


    def login_clicked(self, _):

        self.status.set_text("Logging in...")
        loop.set_alarm_in(0.1, self.login)


    def login(self, *_):

        self.username = self.username_edit.get_edit_text()
        self.password = self.password_edit.get_edit_text()

        try:

            self.refresh_speed_ui(yota(self.username, self.password))

        except:

            self.err_message()
            return

        self.status.set_text("Logged successfully")


    def refresh_speed_ui(self, r):

        data = next(iter(r.values()))
        fields = (
            "speedNumber",
            "speedString",
            "remainNumber",
            "remainString",
            "amountNumber",
            "amountString",
        )
        fmt = "[{}] {} {} ({} {}, {} {})"
        content = []
        group = []
        for step in data["steps"]:

            if step["code"] == data["offerCode"]:

                callback = None

            else:

                callback = self.SpeedChanger(step["code"])

            desc = str.format("{} {} ({} {}, {} {})", *map(lambda k: bs(step[k]).text, fields))
            state = step["code"] == data["offerCode"]
            content.append(urwid.RadioButton(group, desc, state=state, on_state_change=callback))

        content.append(urwid.Button("Refresh", on_press=self.login_clicked))
        self.common_container.original_widget = urwid.Pile(content)


    def err_message(self):

        self.status.set_text("Some error occurs, check for internet connection and valid username/password")


    def SpeedChanger(self, speed):

        def speed_change_clicked(*args):

            self.status.set_text("Changing speed...")
            loop.set_alarm_in(0.1, speed_changer)

        def speed_changer(*args):

            try:

                self.refresh_speed_ui(yota(self.username, self.password, speed))

            except:

                self.err_message()

            self.status.set_text("Speed changed")

        return speed_change_clicked


if __name__ == "__main__":

    ui = YotaUI()
    loop = urwid.MainLoop(
        ui.ui,
    )
    loop.run()
