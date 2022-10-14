from kivy.metrics import sp
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.stacklayout import StackLayout
from kivy.utils import rgba

from modules.dbactions import connectToDatabase, closeDatabaseConnection
from modules.global_vars import cameras_dict, SECONDARY_COLOR, BG_COLOR, detection_dict, actions_dict

rules_container: FloatLayout
last_addnewrule: FloatLayout
title_label: Label


class RulesContainer(StackLayout):
    def __init__(self, **kwargs):
        super(RulesContainer, self).__init__(**kwargs)
        global rules_container
        rules_container = self

    def on_kv_post(self, base_widget):
        self.load_rules()

    def load_rules(self):
        db, cursor = connectToDatabase()

        cursor.execute("SELECT name, rules, actions FROM cameras WHERE rules!=''")
        results = cursor.fetchall()
        for row in results:
            global title_label
            name = row[0]
            rules_str = row[1]
            actions_str = row[2]
            for i in range(len(rules_str)):
                title_label.active_rules += 1
                rule_name = detection_dict.get(int(rules_str[i]))
                action_name = actions_dict.get(int(actions_str[i]))
                rule_creator = NewRuleCreator(isGenerated=True, camera_name=name, rule_name=rule_name,
                                          action_name=action_name)
                self.add_widget(rule_creator)

        closeDatabaseConnection(db, cursor)


class SpinnerButtons(SpinnerOption):
    def __init__(self, **kwargs):
        super(SpinnerButtons, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = SECONDARY_COLOR
        self.font_size: sp(24)
        self.color = BG_COLOR


class CamerasListButton(Spinner):
    def __init__(self, **kwargs):
        super(CamerasListButton, self).__init__(**kwargs)
        self.values = cameras_dict.values()
        self.option_cls = SpinnerButtons
        self.disabled_color = rgba('ff0000')


class ActionsButton(Spinner):
    def __init__(self, **kwargs):
        super(ActionsButton, self).__init__(**kwargs)
        self.values = detection_dict.values()
        self.option_cls = SpinnerButtons
        self.disabled_color = rgba('ff0000')


class SaveButton(Button):
    actionsListButton = ObjectProperty()
    detectionListButton = ObjectProperty()
    camerasListButton = ObjectProperty()

    def __init__(self, **kwargs):
        super(SaveButton, self).__init__(**kwargs)

    def on_press(self):
        if self.actionsListButton.text == '' or self.detectionListButton.text == '' or self.camerasListButton.text == '':
            popup_content = BoxLayout(orientation='vertical')
            popup_content.add_widget(Label(text='You have omitted one or more values in a rule you are trying to save'))
            btn = Button(text="Understood", size_hint_y=.2)
            popup_content.add_widget(btn)
            popup = Popup(size_hint=[None, None], size=[500, 300], title='Warning', content=popup_content)
            btn.bind(on_press=popup.dismiss)
            popup.open()
            return
        db, cursor = connectToDatabase()
        for cID, value in cameras_dict.items():
            if value == self.camerasListButton.text:
                cameraID = cID
        for dID, value in detection_dict.items():
            if value == self.detectionListButton.text:
                detectionID = dID
        for aID, value in actions_dict.items():
            if value == self.actionsListButton.text:
                actionID = aID
        cursor.execute("UPDATE cameras SET rules=concat(rules, '%s'), actions=concat(actions, '%s') WHERE "
                       "generated_id=%s", (detectionID, actionID, cameraID))
        db.commit()
        self.actionsListButton.disabled = True
        self.detectionListButton.disabled = True
        self.camerasListButton.disabled = True
        self.parent.remove_widget(self)
        closeDatabaseConnection(db, cursor)


class DeleteRule(Button):
    actionsListButton = ObjectProperty()
    detectionListButton = ObjectProperty()
    camerasListButton = ObjectProperty()

    def __init__(self, **kwargs):
        super(DeleteRule, self).__init__(**kwargs)

    def on_press(self):
        cameraID = None
        for cID, value in cameras_dict.items():
            if value == self.camerasListButton.text:
                cameraID = cID
        for dID, value in detection_dict.items():
            if value == self.detectionListButton.text:
                detectionID = dID
        for aID, value in actions_dict.items():
            if value == self.actionsListButton.text:
                actionID = aID
        if cameraID is not None:
            db, cursor = connectToDatabase()
            cursor.execute("SELECT rules, actions FROM cameras WHERE generated_id=%s", (cameraID,))
            results = cursor.fetchone()
            rules_str = results[0]
            actions_str = results[1]
            cursor.execute("UPDATE cameras SET rules=%s, actions=%s WHERE generated_id=%s",
                           (rules_str.replace(str(detectionID), ''), actions_str.replace(str(actionID), ''), cameraID))
            db.commit()
            closeDatabaseConnection(db, cursor)


class ActionsButton2(Spinner):
    def __init__(self, **kwargs):
        super(ActionsButton2, self).__init__(**kwargs)
        self.values = actions_dict.values()
        self.option_cls = SpinnerButtons
        self.disabled_color = rgba('ff0000')


class NewRuleCreator(FloatLayout):
    actionsListButton = ObjectProperty()
    detectionListButton = ObjectProperty()
    camerasListButton = ObjectProperty()
    isGenerated = BooleanProperty(False)
    camera_name = StringProperty()
    rule_name = StringProperty()
    action_name = StringProperty()
    save_rule = ObjectProperty()

    def __init__(self, **kwargs):
        super(NewRuleCreator, self).__init__(**kwargs)

    def on_kv_post(self, base_widget):
        delete_rule = self.ids.delete_rule
        delete_rule.bind(on_press=self.delete_pressed)
        if self.isGenerated:
            self.actionsListButton.text = self.action_name
            self.detectionListButton.text = self.rule_name
            self.camerasListButton.text = self.camera_name
            self.actionsListButton.disabled = True
            self.detectionListButton.disabled = True
            self.camerasListButton.disabled = True
            print(self.children)

            self.save_rule.parent.remove_widget(self.save_rule)
            print(self.children)

    def delete_pressed(self, widget):
        self.parent.remove_widget(self)
        global title_label
        title_label.active_rules -= 1


class AddNewRule(FloatLayout):
    def __init__(self, **kwargs):
        super(AddNewRule, self).__init__(**kwargs)
        global last_addnewrule
        last_addnewrule = self


class TitleLabel(Label):
    active_rules = NumericProperty(0)

    def __init__(self, **kwargs):
        super(TitleLabel, self).__init__(**kwargs)
        global title_label
        title_label = self


class AddNewRule_Button(Button):
    def __init__(self, **kwargs):
        super(AddNewRule_Button, self).__init__(**kwargs)

    def on_press(self):
        rl = NewRuleCreator()
        global rules_container, last_addnewrule, title_label
        rules_container.remove_widget(last_addnewrule)
        rules_container.add_widget(rl)
        rules_container.add_widget(last_addnewrule)
        title_label.active_rules += 1