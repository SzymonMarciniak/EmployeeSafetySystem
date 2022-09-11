from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.metrics import sp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from modules import globals
from modules.dbactions import connectToDatabase, closeDatabaseConnection
from modules.globals import MAIN_COLOR, DECORATION_COLOR_NOALPHA, SECONDARY_COLOR
from kivy.garden.iconfonts import icon


class ChooseWorkplaceScreen(Screen):
    workplace_chooser_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        Window.set_system_cursor('arrow')
        globals.hoverEventObjects = []
        # TO BE MADE. It has to be made to get children of this screen and then append them to this array
        self.workplace_chooser_layout.build_layout()


class NewWorkplace(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = .3
        self.color = MAIN_COLOR
        self.text = "+ SETUP NEW WORKPLACE"


class ExistingWorkplace(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = .3
        self.orientation = 'vertical'
        self.padding = 20, 25


class EwTitle(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_x = .9
        self.valign = 'top'
        self.color = SECONDARY_COLOR
        self.font_name = 'Lato'
        self.font_size = sp(24)
        self.bind(size=self.update)

    def update(self, *args):
        self.text_size = self.size


class EwNumber(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_x = .1
        self.valign = 'top'
        self.halign = 'right'
        self.color = SECONDARY_COLOR
        self.font_name = 'Lato'
        self.font_size = sp(24)
        self.bind(size=self.update)

    def update(self, *args):
        self.text_size = self.size


class EwStatus(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.font_size = sp(20)
        self.font_name = 'Lato'
        self.color = [0, 0, 0, 1]
        self.bind(size=self.update)

    def update(self, *args):
        self.text_size = self.size


class EwNotifications(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.font_size = sp(20)
        self.font_name = 'Lato'
        self.color = [0, 0, 0, 1]
        self.bind(size=self.update)

    def update(self, *args):
        self.text_size = self.size


class EwAlerts(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.font_size = sp(20)
        self.font_name = 'Lato'
        self.color = [0, 0, 0, 1]
        self.text = "[color=#08c48c]%s[/color] No new alerts" % icon('zmdi-check')
        self.bind(size=self.update)

    def update(self, *args):
        self.text_size = self.size


class WorkplaceChooserLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 30, 5
        self.size_hint_y = .73

    def build_layout(self):
        db, cursor = connectToDatabase()
        cursor.execute("SELECT name, position, state_activation, state_notifications FROM workplaces WHERE userid=%s "
                       "ORDER BY position ASC;", (globals.userID,))
        results = cursor.fetchall()
        row_count = cursor.rowcount
        closeDatabaseConnection(db, cursor)
        if results is not None:
            for row in results:
                self.buildExistingWorkplace(row[0], row[1], row[2], row[3])
        for i in range(row_count, 3):
            self.buildNewWorkplace()

    def buildExistingWorkplace(self, title, pos, s_activation, s_notifications):
        ew = ExistingWorkplace()
        boxlayout = BoxLayout()
        boxlayout.add_widget(EwTitle(text=title))
        boxlayout.add_widget(EwNumber(text='#'+str(pos)))
        ew.add_widget(boxlayout)
        division = BoxLayout()
        boxlayout = BoxLayout(orientation='vertical', size_hint_x=.8)
        label_text = "[color=%s]%s[/color] " \
                     "Status: %s" % ("#08c48c" if s_activation > 0 else "#c92a1e",
                                     icon('zmdi-circle'), "Active" if s_activation > 0 else "Disabled")
        boxlayout.add_widget(EwStatus(text=label_text))
        label_text = "[color=%s]%s[/color] " \
                     "Notifications: %s" % ("#08c48c" if s_notifications < 0 else "#c92a1e",
                                            icon('zmdi-notifications-off') if s_notifications > 0 else
                                            icon('zmdi-notifications-active'), "Active"
                                            if s_activation > 0 else "Disabled")
        boxlayout.add_widget(EwNotifications(text=label_text))
        # label_text = "[color=%s]%s[/color] " \
        #              "%s" % ("#08c48c" if s_notifications > 0 else "#c92a1e",
        #                      icon('zmdi-') if s_notifications > 0 else
        #                      icon('zmdi-notifications-active'), "No actions to be taken"
        #                      if self.s_activation > 0 else "X alerts active")
        boxlayout.add_widget(EwAlerts())
        division.add_widget(boxlayout)
        boxlayout = BoxLayout(size_hint_x=.2)
        boxlayout.add_widget(RoundedButton(markup=True, text="%s" % icon('zmdi-chevron-right')))
        division.add_widget(boxlayout)
        ew.add_widget(division)
        self.add_widget(ew)

    def buildNewWorkplace(self):
        self.add_widget(NewWorkplace())


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = [0, 0, 0, 0]
        self.font_size = sp(32)