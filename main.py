import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class MyApp(App):
    def build(self):
        self.click_count = 0
        layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Button has been clicked 0 times.")
        button = Button(text="Click me")
        button.bind(on_press=self.on_button_click)
        layout.add_widget(self.label)
        layout.add_widget(button)
        return layout

    def on_button_click(self, instance):
        self.click_count += 1
        self.label.text = f"Button has been clicked {self.click_count} times."

if __name__ == "__main__":
    MyApp().run()