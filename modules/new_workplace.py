from kivy.animation import Animation, AnimationTransition
from kivy.app import App
from kivy.properties import NumericProperty, ColorProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.uix.togglebutton import ToggleButton

from modules.dbactions import insertNewWorkplace
from modules.global_vars import DECORATION_COLOR_NOALPHA, ERROR_COLOR, BG_COLOR


class NewWorkplaceScreen(Screen):
    pass


class StatusToggleButton(ToggleButton):
    p1 = NumericProperty()
    p2 = NumericProperty()
    s1 = NumericProperty()
    s2 = NumericProperty()
    toggle_color = ColorProperty()
    rect_color = ColorProperty()

    def __init__(self, **kwargs):
        super(StatusToggleButton, self).__init__(**kwargs)

    def on_toggled(self, button_obj: ToggleButton):
        if button_obj.state == 'down':
            button_obj.text = "ON"
            anim = Animation(p1=self.x, p2=self.y, s1=self.width, s2=self.height, toggle_color=DECORATION_COLOR_NOALPHA,
                             duration=.8, rect_color=DECORATION_COLOR_NOALPHA, color=BG_COLOR,
                             transition=AnimationTransition.in_out_quad)
            anim.start(button_obj)
        else:
            button_obj.text = "OFF"
            anim = Animation(p1=self.x + self.width / 2, p2=self.y, s1=0, s2=self.height,
                             toggle_color=ERROR_COLOR, rect_color=[0, 0, 0, 0], duration=.8, color=ERROR_COLOR,
                             transition=AnimationTransition.in_out_quad)
            anim.start(button_obj)


class CreateWorkplaceButton(Button):
    workplace_name_textinput = ObjectProperty()
    status_toggle = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rectColor = '#0fafff'

    def on_pressed(self):
        self.rectColor = '#0f87ff'

    def on_released(self):
        self.rectColor = '#0fafff'
        insertNewWorkplace(self.workplace_name_textinput.text, True if self.status_toggle.state == 'down' else False)
        app = App.get_running_app()
        app.root.transition = FadeTransition()
        app.root.current = 'choose_workplace_screen'


class BackToWorkplaceChooserButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rectColor = "#0fafff"

    def on_pressed(self):
        self.rectColor = "#0f87ff"

    def on_released(self):
        self.rectColor = "#0fafff"
        app = App.get_running_app()
        app.root.transition = FadeTransition()
        app.root.current = 'choose_workplace_screen'
