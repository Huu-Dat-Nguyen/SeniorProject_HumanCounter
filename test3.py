import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import ScreenManager, Screen
import os
import subprocess

class Home(BoxLayout):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create buttons for navigation
        self.camera_button = Button(text='Go to Camera', size_hint=(1, 1))
        self.camera_button.bind(on_press=self.go_to_camera)
        self.add_widget(self.camera_button)

        self.footage_button = Button(text='View Footage', size_hint=(1, 1))
        self.footage_button.bind(on_press=self.go_to_manage_footage)
        self.add_widget(self.footage_button)

    def go_to_camera(self, instance):
        App.get_running_app().root.current = 'CameraScreen'

    def go_to_manage_footage(self, instance):
        App.get_running_app().root.current = 'ManageFootageScreen'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.home = Home()
        self.add_widget(self.home)

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        self.camera = Camera(resolution=(1280, 720), play=True)
        self.add_widget(self.camera)

        # Create a button to navigate back to the home screen
        self.home_button = Button(text='Back to Home', size_hint=(1, 0.1))
        self.home_button.bind(on_press=self.go_to_home)
        self.add_widget(self.home_button)

    def go_to_home(self, instance):
        App.get_running_app().root.current = 'MainScreen'

class FootageListView(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create a FileChooserListView to display footage files
        self.filechooser = FileChooserListView(path=os.path.join(os.environ['EXTERNAL_STORAGE'], 'recorded_videos'))
        self.filechooser.bind(on_selection=self.on_select)
        self.add_widget(self.filechooser)

        # Create a layout for the toggle button
        button_layout = BoxLayout(size_hint_y=None, height='50dp')
        self.add_widget(button_layout)

        # Create a button to navigate back to the home screen
        self.home_button = Button(text='Back to Home', size_hint=(1, None), height='50dp')
        self.home_button.bind(on_press=self.go_to_home)
        button_layout.add_widget(self.home_button)

    def on_select(self, filechooser, selection):
        if selection:
            selected_file = selection[0]
            print(f"Selected file: {selected_file}")
            self.go_to_video_player(selected_file)

    def go_to_video_player(self, filepath):
        # Open the video using the default video player on the device
        subprocess.call(['am', 'start', '-a', 'android.intent.action.VIEW', '-d', f'file://{filepath}'])

    def go_to_home(self, instance):
        App.get_running_app().root.current = 'MainScreen'

class ManageFootageScreen(Screen):
    def __init__(self, **kwargs):
        super(ManageFootageScreen, self).__init__(**kwargs)
        self.footage_list = FootageListView()
        self.add_widget(self.footage_list)

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='MainScreen'))
        sm.add_widget(CameraScreen(name='CameraScreen'))
        sm.add_widget(ManageFootageScreen(name='ManageFootageScreen'))
        return sm

if __name__ == '__main__':
    MyApp().run()
