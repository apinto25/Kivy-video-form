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
        if info == "no_exist":
            nonexistent_user_popup()
            self.reset()
        elif info == "correct":
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
            print("Todos los campos están llenitos")
            if not " " in self.user_name.text:
                print("User ok")
                if self.email.text.count("@") == 1 and self.email.text.split("@")[1].count(".") >= 1:
                    print("Email ok")
                    if self.password.text == self.password_again.text:
                        print("Passwords ok")
                        created = user_created(
                            CON, self.full_name.text, self.user_name.text, self.email.text, self.password.text)
                        if created:
                            print("Nostánrepetidos")
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
            buf1 = cv2.flip(frame, 0)
            w, h = frame.shape[1], frame.shape[0]
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(w, h))
                texture.flip_vertical()
            texture.blit_buffer(buf1.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()


CAPTURE = None


# class MainUserWindow(Screen):
#
#    def capture(self):
#        camera = self.ids['camera']
#        timestr = time.strftime("%Y%m%d_%H%M%S")
#        camera.export_to_png("IMG_{}.png".format(timestr))
#        print("Captured")


class MainUserWindow(Screen):

    def init_qrtest(self):
        pass

    def dostart(self, *largs):
        global CAPTURE
        CAPTURE = cv2.VideoCapture("rtsp://admin:admin@192.168.1.104")
#            "/home/watson/Videos/2020-01-17 12-53-12.mp4")
        self.ids.qrcam.start(CAPTURE)

    def doexit(self):
        global CAPTURE
        if CAPTURE != None:
            CAPTURE.release()
            CAPTURE = None
#        EventLoop.close()
        ANA_BANANA.current = "login"


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


def user_login(con, user_name, password):
    cursorObj = con.cursor()
    cursorObj.execute(
        "SELECT password FROM USER WHERE user_name = ?", (user_name,))
    user = cursorObj.fetchone()
    if user is None:
        info = "no_exist"
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
