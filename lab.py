from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button


class StackLayoutExample(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        size = (dp(100), dp(100))
        for i in range(50):
            b = Button(text=f"{i+1}", size_hint=(None, None), size=size)
            self.add_widget(b)


class AnchorLayoutExample(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BoxLayoutExample(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation="vertical"
        b1 = Button(text="A")
        b2 = Button(text="B")


class WidgetsExample(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count = 1
        self.my_text = "1"

    def on_button_click(self):
        self.count += 1
        self.my_text = str(self.count)

class Surfly(App):
    pass


Surfly().run()