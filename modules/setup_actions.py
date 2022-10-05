import math
from kivy.graphics import Ellipse
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.text import LabelBase
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.garden.iconfonts import iconfonts
from kivy import Config


from modules.dbactions import connectToDatabase, closeDatabaseConnection
from modules.global_vars import cameras_dict


class DeleteWidgetPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GetNamePopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        


class Camera(Ellipse):
    def __init__(self,deleteId,name, **kwargs):
        super().__init__(**kwargs)

        self.deleteId = deleteId
        self.name = name
        

class Room(Line):

    def __init__(self, deleteId, name,  **kwargs) -> None:
        super().__init__( **kwargs)
        self.deleteId = deleteId
        self.name = name

class Door(Line):
    def __init__(self, deleteId, **kwargs) -> None:
        super().__init__(**kwargs)
        self.deleteId = deleteId
        
rooms_points = []
rooms_list = []
rooms_names = []

doors_points = []
door_list = []

camera_points = []
cameras_list = []
cameras_names = []

new_created = "None"
new_points = []
new_id = 0

idsLabels = []
nameLabels = []

rooms_to_move = []
doors_to_move = []
cameras_to_move = []

circle1_list = []
circle2_list = []

class SetupScreen(Screen):
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
            self.bind(size=self.cameras_refresh)
            

        self.points = []
        self.end_points = []

        self.double = True

        self.new_cam_id = 1
        self.new_room_id = 100
        self.new_door_id = 200 

        self.load_objects()
       
    
    # def on_kv_post(self, *args):
    #     self.load_objects()
        

    def load_objects(self):

        db, cursor = connectToDatabase()
        cursor.execute("SELECT * FROM rooms")
        rooms_results = cursor.fetchall()

        for load_room in rooms_results:
            with self.canvas.before:
                print(f"askhbasfkihbask {self}")
                Color(255/255,255/255,255/255)
                line = Room(width=1.5, deleteId=load_room[6], name=load_room[5])
            x1, y1, x2, y2 = load_room[1], load_room[2], load_room[3], load_room[4]
            cx1, cx2 = x1*self.width, x2*self.width
            cy1, cy2 = y1*self.height, y2*self.height
            line.points = cx1,cy2,cx1,cy1,cx2,cy1,cx2,cy2,cx1,cy2 
            rooms_points.append((x1, y1, x2, y2))
            rooms_list.append(line)
            if load_room[6] > self.new_room_id:
                self.new_room_id = load_room[6]

        cursor.execute("SELECT * FROM cameras")
        cameras_results = cursor.fetchall()
        for load_camera in cameras_results:
            x1, y1 = load_camera[1], load_camera[2]
            camera_points.append((x1-.254, y1))
            x1 = x1 * self.width
            y1 = y1 * self.height
            with self.canvas:
                Color(1,1,1,1, mode='rgba')
                camera = Camera(pos=(x1, y1), size=(20, 20), deleteId=load_camera[4], name=load_camera[3])
                Color(0,0,0,1, mode='rgba')
                circle1 = Ellipse(pos=(camera.pos[0] + 5, camera.pos[1] + 5), size=(10, 10))
                Color(1,1,1,1, mode='rgba')
                circle2 = Ellipse(pos=(circle1.pos[0] + 2.5, circle1.pos[1] + 2.5), size=(5, 5))

            cameras_names.append(load_camera[3])
            print(x1, y1)
            cameras_list.append(camera)
            cameras_dict[load_camera[4]] = load_camera[3]
            circle1_list.append(circle1)
            circle2_list.append(circle2)
            
            if load_camera[4] > self.new_cam_id:
                self.new_cam_id = load_camera[4]

        cursor.execute("SELECT * FROM doors")
        doors_results = cursor.fetchall()
        for load_door in doors_results:
            with self.canvas.before:
                Color(40/255, 42/255, 53/255)
                line = Door(width=8, deleteId=load_door[5])
            x1, y1, x2, y2 = load_door[1], load_door[2], load_door[3], load_door[4] 
            line.points = x1 * self.width, y1 * self.height, x2 * self.width, y2 *self.height
            doors_points.append((x1, y1, x2, y2))
            door_list.append(line)

            if load_door[5] > self.new_door_id:
                self.new_door_id = load_door[5]

        closeDatabaseConnection(db, cursor)

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
                x1, x2 = ckx1*self.width, ckx2 * self.width
                y1, y2 = cky1 * self.height, cky2* self.height
                door.points = x1, y1, x2, y2
    
    def cameras_refresh(self, *args):
        for id, camera in enumerate(cameras_list):
            p = len(cameras_list) 
            circle1, circle2 = circle1_list[id], circle2_list[id]
            if p != id: 
                ckx1, cky1 = camera_points[id]
                x1 = ckx1*self.width
                y1 = cky1 * self.height
                camera.pos = x1, y1
                circle1.pos = camera.pos[0] + 5, camera.pos[1] + 5
                circle2.pos = circle1.pos[0] + 2.5, circle1.pos[1] + 2.5
                print(x1, y1)
    
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
        
        new_camera.x1 = self.kx1 * self.width
        new_camera.y1 = self.ky1 * self.height
        new_camera.name = "asd"
        

    def show_ids(self, clear=False, show=True):
        global idsLabels
        if clear:
            for label in idsLabels:
                self.floatlayout.remove_widget(label)
            idsLabels = []

        if (self.ids["ShowIDButton"].state == "down") and show:
            self.show_names(clear=True, show=False)
            for nr, room in enumerate(rooms_list):
                ckx1, cky1, ckx2, cky2 = rooms_points[nr]
                x_move = .254
                if nr in rooms_to_move:
                    x_move = 0

                x1, x2 = ckx1 * self.floatlayout.width, ckx2 * self.floatlayout.width
                center_x = ((abs(x1) + abs(x2)) / 2 / self.width) - .5 - x_move

                y1, y2 = cky1 * self.height, cky2 * self.height
                y1, y2 = y1/self.floatlayout.height * self.height, y2/self.floatlayout.height * self.height
                center_y = ((abs(y1) + abs(y2)) /2 /self.height) - .5 

                label = Label(text=str(room.deleteId), pos_hint={"x":center_x ,"y":center_y})
                self.floatlayout.add_widget(label)
                idsLabels.append(label)

            for nr, door in enumerate(door_list):
                ckx1, cky1, ckx2, cky2 = doors_points[nr]
                x_move = .254
                if nr in doors_to_move:
                    x_move = 0

                x1, x2 = ckx1 * self.width, ckx2 * self.width
                center_x = ((x1 + x2) / 2 / self.width) - .5 - x_move
                
                y1, y2 = cky1 * self.height, cky2 * self.height
                y1, y2 = y1/self.floatlayout.height * self.height, y2/self.floatlayout.height * self.height
                center_y = ((abs(y1) + abs(y2)) /2 /self.height) - .5 
                
                label = Label(text=str(door.deleteId), pos_hint={"x":center_x ,"y":center_y})
                self.floatlayout.add_widget(label)
                idsLabels.append(label)

            for nr, camera in enumerate(cameras_list):
                ckx1, cky1 = camera_points[nr]
                x1 = ckx1 * self.width + 10
                center_x = (x1 / self.width) - .5 
                
                y1 = cky1 * self.height 
                y1 = y1/self.floatlayout.height * self.height
                center_y = (y1 /self.height) - .5 - .012
                label = Label(text=str(camera.deleteId), pos_hint={"x":center_x ,"y":center_y})
                self.floatlayout.add_widget(label)
                idsLabels.append(label)
        else:
            for label in idsLabels:
                self.floatlayout.remove_widget(label)
            
            idsLabels = []
    
    def show_names(self, clear=False, show=True):
        global nameLabels
        if clear:
            for label in nameLabels:
                self.floatlayout.remove_widget(label)
            nameLabels = []


        if self.ids["ShowNameButton"].state == "down" and show:
            self.show_ids(clear=True, show=False)
            for nr, room in enumerate(rooms_list):
                x_move = .254
                if nr in rooms_to_move:
                    x_move = 0

                ckx1, cky1, ckx2, cky2 = rooms_points[nr]
                x1, x2 = ckx1 * self.width, ckx2 * self.width
                center_x = ((x1 + x2) / 2 / self.width) - .5 - x_move

                y1, y2 = cky1 * self.height, cky2 * self.height
                y1, y2 = y1/self.floatlayout.height * self.height, y2/self.floatlayout.height * self.height
                center_y = ((abs(y1) + abs(y2)) /2 /self.height) - .5

                label = Label(text=str(room.name), pos_hint={"x":center_x ,"y":center_y})
                self.floatlayout.add_widget(label)
                nameLabels.append(label)

            for nr, camera in enumerate(cameras_list):
                ckx1, cky1 = camera_points[nr]
                
                x1 = ckx1 * self.width + 10
                center_x = (x1 / self.width) - .5 
                
                y1 = cky1 * self.height
                y1 = y1/self.floatlayout.height * self.height
                center_y = (y1 /self.height) - .5 - 0.012

                label = Label(text=str(cameras_names[nr]), pos_hint={"x":center_x ,"y":center_y})
                self.floatlayout.add_widget(label)
                nameLabels.append(label)

        else:
            for label in nameLabels:
                self.floatlayout.remove_widget(label)
            nameLabels = []
            
        
        


    def open_delete_popup(self):
        popup = DeleteWidgetPopup()
        popup.bind(on_dismiss=self.delete_widget)
        popup.open()
    
    def delete_widget(self, popup):
        my_id = popup.ids["deleteWidgetId"].text
        if my_id:
            for nr, room in enumerate(rooms_list):
                if room.deleteId == int(my_id):
                    room.points = -1000, -1000
                    rooms_list.remove(room)
                    rooms_points.pop(nr)

                    db, cursor = connectToDatabase()
                    cursor.execute(f"""DELETE FROM rooms WHERE generated_id={my_id}""")
                    db.commit()
                    closeDatabaseConnection(db, cursor)

                    self.show_ids(clear=True)
            
            for nr, camera in enumerate(cameras_list):
                if camera.deleteId == int(my_id):
                    camera.pos_hint = {"x": -10, "y":-10}
                    cameras_list.remove(camera)
                    camera_points.pop(nr)
                    cameras_dict.pop(int(my_id))
                    c1 = circle1_list.pop(nr)
                    c2 = circle2_list.pop(nr)
                    
                    camera.pos = -1000, -1000
                    c1.pos = -1000, -1000
                    c2.pos = -1000, -1000

                    db, cursor = connectToDatabase()
                    cursor.execute(f"""DELETE FROM cameras WHERE generated_id={my_id}""")
                    db.commit()
                    closeDatabaseConnection(db, cursor)

                    self.show_ids(clear=True)
                    self.cameras_refresh()

            for nr, door in enumerate(door_list):
                if door.deleteId == int(my_id):
                    door.points = -1000, -1000
                    door_list.remove(door)
                    doors_points.pop(nr)

                    db, cursor = connectToDatabase()
                    cursor.execute(f"""DELETE FROM doors WHERE generated_id={my_id}""")
                    db.commit()
                    closeDatabaseConnection(db, cursor)

                    self.show_ids(clear=True)
    
    def get_object_name(self, object, points):
        global new_created, new_points
        new_created = object
        new_points = points

        popup = GetNamePopup()
        popup.bind(on_dismiss=self.set_object_name)
        popup.open()
        

    def set_object_name(self, popup):
        new_name = popup.ids["getNameText"].text
        print(f"asdasdasdasd {new_name},,,,, {self}")
        if new_created == "camera":

            with self.canvas:
                Color(1,1,1,1, mode='rgba')
                camera = Camera(size=(20, 20), deleteId=self.new_cam_id, name=new_name)
                cameras_dict[self.new_cam_id] = new_name
                Color(0,0,0,1, mode='rgba')
                circle1 = Ellipse(size=(10, 10))
                Color(1,1,1,1, mode='rgba')
                circle2 = Ellipse(size=(5, 5))

            cameras_names.append(new_name)
            cameras_list.append(camera)
            circle1_list.append(circle1)
            circle2_list.append(circle2)
            cameras_to_move.append(len(cameras_list)-1)

            db, cursor = connectToDatabase()
            cursor.execute(f"""INSERT INTO cameras VALUES (null, {new_points[0]}, {new_points[1]}, '{new_name}' ,{new_id}, '')""")
            db.commit()
            closeDatabaseConnection(db, cursor)
            cameras_names.append(new_name)
            print(camera_points)
            self.cameras_refresh()
        elif new_created == "room":

            with self.canvas.before:
                Color(200/255,200/255,200/255)
                line = Room(width=1.5, deleteId=self.new_room_id, name=new_name)
            rooms_list.append(line)
            rooms_names.append(new_name)
            rooms_to_move.append(len(rooms_list)-1)

            db, cursor = connectToDatabase()
            cursor.execute(f"""INSERT INTO rooms VALUES (null, {new_points[0]}, {new_points[1]}, {new_points[2]}, {new_points[3]}, '{new_name}' ,{new_id})""")
            db.commit()
            closeDatabaseConnection(db, cursor)
            self.rooms_refresh()

        self.show_names(clear=True)
        
        


        
    def on_touch_down(self, touch):
        global new_id
        if super(SetupScreen, self).on_touch_down(touch): #If clicking not in create room zone 
            self.up = False
            return False

        self.up = True
        if self.choose == "new_room":         
                
            self.new_room_id += 1
            new_id = self.new_room_id
            if self.new_room_id == 199: self.new_room_id = 100
            touch.grab(self)
            x =  touch.pos[0]/ self.width
            y = touch.pos[1] / self.height
            self.points = (x, y)
            self.end_points = (x,y)
            self.create_room_function()

        elif self.choose == "create_door":
            self.new_door_id += 1
            new_id = self.new_door_id
            if self.new_door_id == 299: self.new_door_id = 200
            touch.grab(self)
            x =  touch.pos[0]/ self.width
            y = touch.pos[1] / self.height
            self.points = (x, y)
            self.end_points = (x,y)
            self.create_door_function()

        elif self.choose == "add_camera":
            touch.grab(self)
            x =  touch.pos[0]/ self.width
            y = touch.pos[1] / self.height
            self.points = (x, y)

            self.new_cam_id += 1
            new_id = self.new_cam_id
            if self.new_cam_id == 99: self.new_cam_id = 1

            self.kx1, self.ky1 = self.points
                
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
                rooms_points.append([self.kx1-.254,self.ky1,self.kx2-.254,self.ky2])
                self.main_room.points = 0,0
                self.show_ids(clear=True)
                self.get_object_name("room", [self.kx1,self.ky1,self.kx2,self.ky2])
                self.rooms_refresh()
                
        
        if self.choose == "create_door":
            self.double = not self.double  
            if self.double:
                self.main_door.points = 0,0
                self.show_ids(clear=True)

                db, cursor = connectToDatabase()
                cursor.execute(f"""INSERT INTO doors VALUES (null, {self.kx1}, {self.ky1}, {self.kx2}, {self.ky2} ,{new_id})""")
                db.commit()
                closeDatabaseConnection(db, cursor)

                with self.canvas.before:
                    Color(40/255, 42/255, 53/255)
                    door = Door(width=8, cap="square", deleteId=self.new_door_id)
                door_list.append(door)
                doors_points.append([self.kx1-.254,self.ky1,self.kx2-.254,self.ky2])
                doors_to_move.append(len(door_list)-1)

                self.doors_refresh()

        if self.choose == "add_camera":
            self.double = not self.double  
            if self.double:
                camera_points.append([self.kx1-.254,self.ky1])

                self.show_ids(clear=True)
                self.get_object_name("camera", [self.kx1,self.ky1])