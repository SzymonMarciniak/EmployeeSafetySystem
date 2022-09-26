from turtle import width
from kivy.app import App 
import math
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.text import LabelBase
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.garden.iconfonts import iconfonts
from kivy import Config

from utils import CenterOfLine

class camera(Button):
    x1 = NumericProperty()
    y1 = NumericProperty()
    deleteId = NumericProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)



class DeleteWidgetPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setup = SetupScreen()

    def delete_widget(self):
        
        my_id = self.ids.deleteWidgetId.text
        self.setup.delete_widget(my_id)
        self.dismiss()


class Room(Line):

    def __init__(self, deleteId, **kwargs) -> None:
        super().__init__( **kwargs)
        self.deleteId = deleteId

class Door(Line):
    def __init__(self, deleteId, **kwargs) -> None:
        super().__init__(**kwargs)
        self.deleteId = deleteId
        
rooms_points = []
rooms_list = []

doors_points = []
camera_points = []

door_list = []
cameras_list = []

class SetupScreen(BoxLayout):
    floatlayout = ObjectProperty()
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        LabelBase.register(name='Lato',
                           fn_regular='fonts/Lato-Regular.ttf',
                           fn_bold='fonts/Lato-Bold.ttf')
        iconfonts.register("default_font", 'fonts/Material-Design-Iconic-Font.ttf', 'fonts/zmd.fontd')
        Config.set('kivy', 'default_font', 'Lato')

        self.choose = "None"
        with self.canvas.before:
            Color(200/255,200/255,200/255)
            self.main_room = Line(width=1.5)
            self.bind(size=self.rooms_refresh)
            Color(100/250,100/250,100/250)
            self.main_door = Line(width=8,cap="square")
            self.bind(size=self.doors_refresh)

        self.points = []
        self.end_points = []

        self.double = True

        self.new_cam_id = 1
        self.new_room_id = 100
        self.new_door_id = 200 

        self.idsLabels = []

    def create_room_activate(self):
        if self.ids["CreateRoomButton"].state == "down":
            self.choose = "new_room"
        else:
            self.choose = "spectate"
        
    def rooms_refresh(self, *args):
        for id, line in enumerate(rooms_list):
            p = len(rooms_list) 
            if p != id:
                ckx1, cky1, ckx2, cky2 = rooms_points[id]
                x1, x2 = ckx1 * self.width, ckx2 * self.width
                y1, y2 = cky1 * self.height, cky2 * self.height
                line.points = x1,y2,x1,y1,x2,y1,x2,y2,x1,y2 
                
    
    def create_room_function(self, *args):
        self.kx1, self.ky1 = self.points
        self.x1 = self.width * self.kx1
        self.y1 = self.height * self.ky1

        self.kx2, self.ky2 = self.end_points
        self.x2 = self.width * self.kx2
        self.y2 = self.height * self.ky2
        
        self.main_room.points = self.x1,self.y2,self.x1,self.y1,self.x2,self.y1,self.x2,self.y2,self.x1,self.y2 
        #center_x_top, center_y_top = CenterOfLine((self.kx2, self.kx1),(self.ky2,self.ky1), self.width, self.height)
        # center_x_left, center_y_left = CenterOfLine((self.kx1,self.ky2),(self.kx1,self.ky1), self.width, self.height)
        print(f"Distance: x:{float(math.sqrt((self.kx2-self.kx1)**2)/10) * 1000:.1f}m y:{float(math.sqrt((self.ky2-self.ky1)**2)/10) * 1000:.1f}m")
        #Label(text=f"{float(math.sqrt((self.kx2-self.kx1)**2)/10) * 1000:.1f}", pos_hint={'x': center_x_top, 'y': center_y_top }, color=[0.56, 0.56, 0.24, 1], font_size='20sp')
           
    def create_door_activate(self):
        if self.ids["CreateDoorButton"].state == "down":
            self.choose = "create_door"
        else:
            self.choose = "spectate"
    
    def doors_refresh(self, *args):
        for id, door in enumerate(door_list):
            p = len(door_list) 
            if p != id: 
                ckx1, cky1, ckx2, cky2 = doors_points[id]
                x1, x2 = ckx1 * self.width, ckx2 * self.width
                y1, y2 = cky1 * self.height, cky2 * self.height
                door.points = x1, y1, x2, y2
    
    def create_door_function(self, *args):
        self.kx1, self.ky1 = self.points
        self.x1 = self.width * self.kx1
        self.y1 = self.height * self.ky1

        self.kx2, self.ky2 = self.end_points
        self.x2 = self.width * self.kx2
        self.y2 = self.height * self.ky2
        
        self.main_door.points = self.x1, self.y1, self.x2, self.y2
        

    def add_camera_activate(self):
        if self.ids["CreateCameraButton"].state == "down":
            self.choose = "add_camera"
        else:
            self.choose = "spectate"
        
    def add_camera_function(self, new_camera):
        self.kx1, self.ky1 = self.points
        
        new_camera.x1 = self.kx1
        new_camera.y1 = self.ky1
        new_camera.name = "asd"
        

    def show_ids(self, clear=False, show=False):
        if clear:
            for label in self.idsLabels:
                self.floatlayout.remove_widget(label)
            self.idsLabels = []

        if (self.ids["ShowIDButton"].state == "down") or show:
            for nr, room in enumerate(rooms_list):
                ckx1, cky1, ckx2, cky2 = rooms_points[nr]
                x1, x2 = ckx1 * self.width, ckx2 * self.width
                center_x = ((x1 + x2) / 2 / self.width) - .5

                y1, y2 = cky1 * self.height, cky2 * self.height
                y1, y2 = y1/self.floatlayout.height * self.height, y2/self.floatlayout.height * self.height
                center_y = ((abs(y1) + abs(y2)) /2 /self.height) - .5
                label = Label(text=str(room.deleteId), pos_hint={"x":center_x ,"y":center_y})
                self.floatlayout.add_widget(label)
                self.idsLabels.append(label)

            for nr, door in enumerate(door_list):
                ckx1, cky1, ckx2, cky2 = doors_points[nr]
                x1, x2 = ckx1 * self.width, ckx2 * self.width
                center_x = ((x1 + x2) / 2 / self.width) - .5 
                
                y1, y2 = cky1 * self.height, cky2 * self.height
                y1, y2 = y1/self.floatlayout.height * self.height, y2/self.floatlayout.height * self.height
                center_y = ((abs(y1) + abs(y2)) /2 /self.height) - .5
                
                label = Label(text=str(door.deleteId), pos_hint={"x":center_x ,"y":center_y})
                self.floatlayout.add_widget(label)
                self.idsLabels.append(label)

            for nr, camera in enumerate(cameras_list):
                ckx1, cky1 = camera_points[nr]
                x1 = ckx1 * self.width
                center_x = (x1 / self.width) - .5
                
                y1 = cky1 * self.height
                center_y = (y1 /self.height) - .5 - 0.03
                label = Label(text=str(camera.deleteId), pos_hint={"x":center_x ,"y":center_y})
                self.floatlayout.add_widget(label)
                self.idsLabels.append(label)
        else:
            for label in self.idsLabels:
                self.floatlayout.remove_widget(label)
            
            self.idsLabels = []
        


    def open_popup(self):
        DeleteWidgetPopup().open()
    
    def delete_widget(self, my_id):
        for nr, room in enumerate(rooms_list):
            if room.deleteId == int(my_id):
                room.points = -1000, -1000
                rooms_list.remove(room)
                rooms_points.pop(nr)
                self.show_ids(clear=True, show=True)
        
        for nr, camera in enumerate(cameras_list):
            if camera.deleteId == int(my_id):
                camera.pos_hint = {"x": -10, "y":-10}
                cameras_list.remove(camera)
                camera_points.pop(nr)
                self.show_ids(clear=True, show=True)

        for nr, door in enumerate(door_list):
            if door.deleteId == int(my_id):
                door.points = -1000, -1000
                door_list.remove(door)
                doors_points.pop(nr)
                self.show_ids(clear=True, show=True)


        
    def on_touch_down(self, touch):
        if super(SetupScreen, self).on_touch_down(touch): #If clicking not in create room zone 
            self.up = False
            return False

        self.up = True
        if self.choose == "new_room":

            with self.canvas.before:
                Color(200/255,200/255,200/255)
                line = Room(width=1.5, deleteId=self.new_room_id)
                
            self.new_room_id += 1
            if self.new_room_id == 199: self.new_room_id = 100
            rooms_list.append(line)
            touch.grab(self)
            x =  touch.pos[0]/ self.width
            y = touch.pos[1] / self.height
            self.points = (x, y)
            self.end_points = (x,y)
            self.create_room_function()

        elif self.choose == "create_door":
            with self.canvas.before:
                Color(0/255,0/255,0/255)
                door = Door(width=8, cap="square", deleteId=self.new_door_id)
            self.new_door_id += 1
            if self.new_door_id == 299: self.new_door_id = 200
            door_list.append(door)
            touch.grab(self)
            x =  touch.pos[0]/ self.width
            y = touch.pos[1] / self.height
            self.points = (x, y)
            self.end_points = (x,y)
            self.create_door_function()

        elif self.choose == "add_camera":
            new_camera = camera(size_hint = (0,0), deleteId=self.new_cam_id)
            self.new_cam_id += 1
            if self.new_cam_id == 99: self.new_cam_id = 1
            cameras_list.append(new_camera)
            self.floatlayout.add_widget(new_camera)
            touch.grab(self)
            x =  touch.pos[0]/ self.width
            y = touch.pos[1] / self.floatlayout.height
            self.points = (x, y)
            self.add_camera_function(new_camera)

    def on_touch_move(self, touch):
        if self.choose == "new_room":
            if touch.grab_current is self:
                x =  touch.pos[0]/ self.width
                y = touch.pos[1] / self.height
                self.end_points = (x,y)
                self.create_room_function()

        elif self.choose == "create_door":
            if touch.grab_current is self:
                x =  touch.pos[0]/ self.width
                y = touch.pos[1] / self.height
                self.end_points = (x,y)
                self.create_door_function()

        return super(SetupScreen, self).on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if not self.up: #If clicking not in create room zone 
            return False 
            
        if self.choose == "new_room":
            self.double = not self.double  
            if self.double:
                rooms_points.append([self.kx1,self.ky1,self.kx2,self.ky2])
                self.main_room.points = 0,0
                self.rooms_refresh()
                self.show_ids(clear=True)
        
        if self.choose == "create_door":
            self.double = not self.double  
            if self.double:
                doors_points.append([self.kx1,self.ky1,self.kx2,self.ky2])
                self.main_door.points = 0,0
                self.doors_refresh()
                self.show_ids(clear=True)

        if self.choose == "add_camera":
            self.double = not self.double  
            if self.double:
                camera_points.append([self.kx1,self.ky1])
                self.show_ids(clear=True)
                
                
class EmployeeSystemApp(App):
    pass

EmployeeSystemApp().run()






















