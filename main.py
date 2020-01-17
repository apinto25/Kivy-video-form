from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import time


class WindowManager(ScreenManager):
    pass


class LoginWindow(Screen):
    user_name = ObjectProperty(None)
    password = ObjectProperty(None)

    def submit(self):
        if self.user_name.text == "ana" and self.password.text == "banana":
            self.reset()
            ANA_BANANA.current = "main"
        else:
            invalid_login()
            self.reset()

    def create_user(self):
        ANA_BANANA.current = "new_user"
        self.reset()

    def reset(self):
        self.user_name.text = ""
        self.password.text = ""


class NewUserWindow(Screen):
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
                        if self.user_name.text != "ana" or self.email.text != "ana@banana.com":
                            print("Nostánrepetidos")
                            correctly_created(self.user_name.text)
                            ANA_BANANA.current = "login"
                            self.reset()
                        else:
                            user_already_exists()
                    else:
                        passwords_dont_match()
                else:
                    invalid_email()
            else:
                user_with_sapces()
        else:
            empty_fields()

    def go_login(self):
        ANA_BANANA.current = "login"

    def reset(self):
        self.full_name.text = ""
        self.user_name.text = ""
        self.email.text = ""
        self.password.text = ""
        self.password_again.text = ""


class MainUserWindow(Screen):

    def capture(self):
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png("IMG_{}.png".format(timestr))
        print("Captured")


def user_with_sapces():
    pop = Popup(title="Usuario inválido",
                content=Label(text='El usuario no debe\ncontener espacios.'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def empty_fields():
    pop = Popup(title="Campos vacíos",
                content=Label(text='Uno o más campos\nestán vacíos.'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def user_already_exists():
    pop = Popup(title="El usuario ya existe",
                content=Label(
                    text='El usuario o el email ya\nse encuentran registrados.'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def invalid_email():
    pop = Popup(title="Email inválido",
                content=Label(
                    text='Formato de correo\nelectrónico incorrecto'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def passwords_dont_match():
    pop = Popup(title="Contraseña incorrecta",
                content=Label(text='Las contraseñas no\ncoinciden'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def correctly_created(user_name):
    pop = Popup(title="Usuario creado",
                content=Label(text='Usuario ' + user_name + 'creado'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


def invalid_login():
    pop = Popup(title="",
                content=Label(text='Usuario o contraseña incorrectos.'),
                size_hint=(None, None), size=(300, 150))
    pop.open()


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
