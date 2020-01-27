from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.base import EventLoop
import time
import cv2
import sqlite3


class WindowManager(ScreenManager):
    pass


class LoginWindow(Screen):
    global CON
    user_name = ObjectProperty(None)
    password = ObjectProperty(None)

    def submit(self):
        info = user_login(CON, self.user_name.text, self.password.text)
        if info == "non_existent":
            nonexistent_user_popup()
            self.reset()
        elif info == "correct":
            mainw = self.manager.get_screen("main")
            full_name = get_full_name(CON, self.user_name.text)
            mainw.update_title("Welcome " + full_name[0])
            self.reset()
            ANA_BANANA.current = "main"
        else:
            invalid_login_popup()
            self.reset()

    def create_user(self):
        ANA_BANANA.current = "new_user"
        self.reset()

    def reset(self):
        self.user_name.text = ""
        self.password.text = ""


class NewUserWindow(Screen):
    global CON
    full_name = ObjectProperty(None)
    user_name = ObjectProperty(None)
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    password_again = ObjectProperty(None)

    def create_user(self):
        fields = [
            self.full_name.text,
            self.user_name.text,
            self.email.text,
            self.password.text,
            self.password_again.text
        ]

        result = ["empty" for field in fields if not field.strip()]

        if len(result) == 0:
            if not " " in self.user_name.text:
                if self.email.text.count("@") == 1 and self.email.text.split("@")[1].count(".") >= 1:
                    if self.password.text == self.password_again.text:
                        created = user_created(
                            CON, self.full_name.text, self.user_name.text, self.email.text, self.password.text)
                        if created:
                            self.reset()
                            correctly_created_popup(self.user_name.text)
                            ANA_BANANA.current = "login"
                        else:
                            user_exists_popup()
                    else:
                        diff_passwords_popup()
                else:
                    invalid_email_popup()
            else:
                user_spaces_popup()
        else:
            empty_fields_popup()

    def go_login(self):
        ANA_BANANA.current = "login"
        self.reset()

    def reset(self):
        self.full_name.text = ""
        self.user_name.text = ""
        self.email.text = ""
        self.password.text = ""
        self.password_again.text = ""


class KivyCamera(Image):

    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = None

    def start(self, capture, fps=30):
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def stop(self):
        Clock.unschedule_interval(self.update)
        self.capture = None

    def update(self, dt):
        return_value, frame = self.capture.read()
        if return_value:
            texture = self.texture
            frame = cv2.resize(frame, (350, 350))
            #buf1 = cv2.flip(frame, 0)
            w, h = frame.shape[1], frame.shape[0]
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(w, h))
                texture.flip_vertical()
            texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()


CAM1 = None
CAM2 = None

class MainUserWindow(Screen):
    title = ObjectProperty(None)

    def init_qrtest(self):
        pass

    def dostart(self, *largs):
        global CAM1, CAM2
        CAM1 = cv2.VideoCapture("videos/flower_field.mp4")
        CAM2 = cv2.VideoCapture("videos/landscape.mp4")
        self.ids.qrcam.start(CAM1)
        self.ids.qrcam_one.start(CAM2)


    def doexit(self):
        global CAM1, CAM2
        if CAM1 != None:
            CAM1.release()
            CAM1 = None
        if CAM2 != None:
            CAM2.release()
            CAM2 = None
        ANA_BANANA.current = "login"

    def update_title(self, message):
        self.title.text = message

def user_spaces_popup():
    pop = Popup(title="Usuario inválido",
                content=Label(text='El usuario no debe\ncontener espacios.'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def empty_fields_popup():
    pop = Popup(title="Campos vacíos",
                content=Label(text='Uno o más campos\nestán vacíos.'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def user_exists_popup():
    pop = Popup(title="El usuario ya existe",
                content=Label(
                    text='El usuario o el email ya\nse encuentran registrados.'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def invalid_email_popup():
    pop = Popup(title="Email inválido",
                content=Label(
                    text='Formato de correo\nelectrónico incorrecto'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def diff_passwords_popup():
    pop = Popup(title="Contraseña incorrecta",
                content=Label(text='Las contraseñas no\ncoinciden'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def correctly_created_popup(user_name):
    pop = Popup(title="Usuario creado",
                content=Label(text='Usuario ' + user_name + ' creado'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def invalid_login_popup():
    pop = Popup(title="",
                content=Label(text='Usuario o contraseña incorrectos.'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def nonexistent_user_popup():
    pop = Popup(title="El usuario no existe",
                content=Label(
                    text='El usuario ingresado no se\nencuentra registrado.'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def user_created(con, full_name, user_name, email, password):
    cursorObj = con.cursor()
    cursorObj.execute(
        """SELECT user_name, email FROM USER
        WHERE user_name = ? OR email = ?""",
        (user_name, email)
    )
    rows = cursorObj.fetchall()
    if len(rows) == 0:
        cursorObj.execute(
            """INSERT INTO USER (full_name, user_name, email, password) 
            VALUES(?, ?, ?, ?)""",
            (full_name, user_name, email, password)
        )
        created = True
    else:
        created = False

    con.commit()
    return created

def get_full_name(con, user_name):
    cur = con.cursor()
    cur.execute(
        """SELECT full_name FROM USER
        WHERE user_name = ?""",
        (user_name,)
    )
    full_name = cur.fetchone()
    return full_name

def user_login(con, user_name, password):
    cursorObj = con.cursor()
    cursorObj.execute(
        "SELECT password FROM USER WHERE user_name = ?", (user_name,))
    user = cursorObj.fetchone()
    if user is None:
        info = "non_existent"
    elif user[0] == password:
        info = "correct"
    else:
        info = "incorrect"

    return info


CON = sqlite3.connect('DB/users.db')

Window.size = (480, 480)
KV = Builder.load_file("custom.kv")
ANA_BANANA = WindowManager()
SCREENS = [
    LoginWindow(name="login"),
    NewUserWindow(name="new_user"),
    MainUserWindow(name="main")
]

for screen in SCREENS:
    ANA_BANANA.add_widget(screen)

ANA_BANANA.current = "login"


class MyCustomApp(App):
    def build(self):
        return ANA_BANANA


if __name__ == "__main__":
    MyCustomApp().run()
