import kivy
from datetime import datetime
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.graphics.texture import Texture
import os
import cv2
import subprocess

class Home(BoxLayout):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create a GridLayout for the buttons
        button_layout = GridLayout(cols=1, rows=4, size_hint=(1, 0.8))
        self.add_widget(button_layout)

        # Create buttons for navigation
        self.camera_button = Button(text='Go to CameraScreen', size_hint=(1, 1))
        self.camera_button.bind(on_press=self.go_to_camera)
        button_layout.add_widget(self.camera_button)

        self.footage_button = Button(text='Manage Footage', size_hint=(1, 1))
        self.footage_button.bind(on_press=self.go_to_manage_footage)
        button_layout.add_widget(self.footage_button)

        # Placeholder buttons
        self.placeholder1_button = Button(text='Placeholder 1', size_hint=(1, 1))
        self.placeholder1_button.bind(on_press=self.go_to_placeholder1)
        button_layout.add_widget(self.placeholder1_button)

        self.placeholder2_button = Button(text='Placeholder 2', size_hint=(1, 1))
        self.placeholder2_button.bind(on_press=self.go_to_placeholder2)
        button_layout.add_widget(self.placeholder2_button)
    
    def go_to_camera(self, instance):
        App.get_running_app().root.current = 'CameraScreen'

    def go_to_manage_footage(self, instance):
        App.get_running_app().root.current = 'ManageFootageScreen'

    def go_to_placeholder1(self, instance):
        App.get_running_app().root.current = 'PlaceHolder2'

    def go_to_placeholder2(self, instance):
        App.get_running_app().root.current = 'PlaceHolder3'    

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.home = Home()
        self.add_widget(self.home)

class CameraFeed(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraFeed, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create a Camera widget to show the video feed
        self.camera = Camera(resolution=(1280, 720), play=True)  # Adjust resolution for mobile
        self.add_widget(self.camera)

        # Set directory for storing videos
        self.storage_dir = os.path.join(os.getcwd(), 'recorded_videos')
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

        # Initialize recording variables
        self.recording = False
        self.out = None
        self.status_label = None

        # Create a layout for the toggle button
        button_layout = BoxLayout(size_hint_y=None, height='50dp')
        self.add_widget(button_layout)

        # Create the "Start/Stop Recording" toggle button
        self.toggle_button = Button(text='Start Recording', size_hint=(1, None), height='50dp')
        self.toggle_button.bind(on_press=self.toggle_recording)
        button_layout.add_widget(self.toggle_button)

        # Create a button to navigate to the footage management screen
        self.home_button = Button(text='Home', size_hint=(1, None), height='50dp')
        self.home_button.bind(on_press=self.go_to_home)
        button_layout.add_widget(self.home_button)

    # Method to toggle video recording
    def toggle_recording(self, instance):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    # Method to start video recording
    def start_recording(self):
        self.recording = True
        self.display_status('Recording started')

        # Start capturing video using OpenCV
        self.cap = cv2.VideoCapture(0)  # Mobile devices may need to specify the camera index
        
        if not self.cap.isOpened():
            self.display_status('Error: Camera could not be opened!')
            return
        
        # Set the resolution for better quality
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Get current timestamp and set video output file path
        filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        filepath = os.path.join(self.storage_dir, filename)

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(filepath, fourcc, 20.0, (1280, 720))

        # Schedule the update function to capture frames periodically
        Clock.schedule_interval(self.update, 1.0 / 20.0)  # 20 FPS
        self.toggle_button.text = 'Stop Recording'  # Update button text

    # Method to stop video recording
    def stop_recording(self):
        self.recording = False
        self.display_status('Recording stopped')

        # Stop capturing and release resources
        Clock.unschedule(self.update)
        if self.cap is not None:
            self.cap.release()
        if self.out is not None:
            self.out.release()

        self.toggle_button.text = 'Start Recording'  # Update button text

    # Method to capture frames and write to video file
    def update(self, dt):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Write the frame to the video file
                self.out.write(frame)
                
                # Convert the frame to a texture and display it
                buf = cv2.flip(frame, 0)  # Flip vertically
                buf = buf.tobytes()  # Convert to bytes
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.camera.texture = texture  # Update the camera widget
            else:
                self.display_status('Error: Could not read frame.')

    # Method to display status label
    def display_status(self, text):
        # Create status label if it doesn't exist
        if self.status_label is None:
            self.status_label = Label(text=text, size_hint_y=None, height='50dp')
            self.add_widget(self.status_label)
        else:
            self.status_label.text = text  # Update existing label text

        # Schedule the removal of the label after 2 seconds
        Clock.schedule_once(self.remove_status_label, 2)

    # Method to remove status label
    def remove_status_label(self, dt):
        if self.status_label:
            self.remove_widget(self.status_label)
            self.status_label = None

    # Method to navigate to the Manage Footage screen
    def go_to_home(self, instance):
        App.get_running_app().root.current = 'MainScreen'

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        self.camera_feed = CameraFeed()
        self.add_widget(self.camera_feed)

class FootageListView(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create a FileChooserListView to display footage files
        self.filechooser = FileChooserListView(path=os.path.join(os.getcwd(), 'recorded_videos'))
        self.filechooser.bind(on_selection=self.on_select)
        self.add_widget(self.filechooser)

        # Create a layout for the toggle button
        button_layout = BoxLayout(size_hint_y=None, height='50dp')
        self.add_widget(button_layout)

        # Create a button to navigate to the footage management screen
        self.home_button = Button(text='Home', size_hint=(1, None), height='50dp')
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
