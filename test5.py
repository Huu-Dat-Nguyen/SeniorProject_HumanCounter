from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from plyer import camera

class CameraApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        capture_button = Button(text='Capture Image')
        capture_button.bind(on_press=self.capture_image)
        layout.add_widget(capture_button)
        return layout

    def capture_image(self, instance):
        camera.take_picture(self.on_picture_taken)

    def on_picture_taken(self, filepath):
        print(f'Image saved to: {filepath}')

if __name__ == '__main__':
    CameraApp().run()
