import kivy
import cv2
from datetime import datetime
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.video import Video
from kivy.graphics.texture import Texture
import os

from matplotlib.widgets import Slider

class Home(BoxLayout):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create a GridLayout for the buttons
        button_layout = GridLayout(cols=1, rows=4, size_hint=(1, 0.8))  # 2 columns, 2 rows
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
        
        # Set a responsive size for the app window
        Window.size = (360, 640)  # Might be optional, consider using size_hint

        # Create the CameraFeed component and add it to the screen
        self.home = Home()
        self.add_widget(self.home)

class CameraFeed(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraFeed, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create an Image widget to show the video feed
        self.video_display = Image(size_hint=(1, 0.8))  # Take 80% of the height
        self.add_widget(self.video_display)
        
        # Set directory for storing videos
        self.storage_dir = os.path.join(os.getcwd(), 'recorded_videos')
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

        # Initialize recording variables
        self.recording = False
        self.out = None
        self.cap = None
        self.status_label = None  # Initialize status_label to None

        # Create a layout for the toggle button
        button_layout = BoxLayout(size_hint_y=None, height='50dp')
        self.add_widget(button_layout)

        # Create the "Start/Stop Recording" toggle button
        self.toggle_button = Button(text='Start Recording', size_hint=(1, None), height='50dp')  # Full width
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
        self.cap = cv2.VideoCapture(0)  # Open webcam
        if not self.cap.isOpened():
            self.display_status('Error: Camera could not be opened!')
            return
        
        # Set the resolution for better quality
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Set width to 1280
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Set height to 720
        
        # Get current timestamp and set video output file path
        filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        filepath = os.path.join(self.storage_dir, filename)

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(filepath, fourcc, 20.0, (1280, 720))  # Match the resolution

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
                self.video_display.texture = texture  # Update the image widget
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
        Clock.schedule_once(self.remove_status_label, 2)  # Change 2 to the desired duration

    # Method to remove status label
    def remove_status_label(self, dt):
        if self.status_label:
            self.remove_widget(self.status_label)
            self.status_label = None  # Reset the status_label to None

    # Method to navigate to the Manage Footage screen
    def go_to_home(self, instance):
        App.get_running_app().root.current = 'MainScreen'

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        
        # Set a responsive size for the app window
        Window.size = (360, 640)  # Might be optional, consider using size_hint

        # Create the CameraFeed component and add it to the screen
        self.camera_feed = CameraFeed()
        self.add_widget(self.camera_feed)

class VideoPlayer(BoxLayout):
    def __init__(self, **kwargs):
        super(VideoPlayer, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create a VideoPlayer widget
        self.video_player = VideoPlayer(state='stop', options={'eos': 'stop'})
        self.add_widget(self.video_player)
        
        # Create a layout for controls
        self.control_layout = BoxLayout(size_hint_y=None, height='50dp')
        self.add_widget(self.control_layout)

        # Play/Pause button
        self.play_button = Button(text='Play', size_hint=(None, 1), width='100dp')
        self.play_button.bind(on_press=self.toggle_play)
        self.control_layout.add_widget(self.play_button)

        # Rewind button
        self.rewind_button = Button(text='Rewind', size_hint=(None, 1), width='100dp')
        self.rewind_button.bind(on_press=self.rewind_video)
        self.control_layout.add_widget(self.rewind_button)

        # Fast Forward button
        self.fast_forward_button = Button(text='Fast Forward', size_hint=(None, 1), width='100dp')
        self.fast_forward_button.bind(on_press=self.fast_forward_video)
        self.control_layout.add_widget(self.fast_forward_button)

        # Duration Slider
        self.progress_bar = Slider(min=0, max=100, value=0)
        self.progress_bar.bind(value=self.seek_video)
        self.control_layout.add_widget(self.progress_bar)

        # Duration label
        self.duration_label = Label(text="00:00 / 00:00", size_hint=(None, 1), width='120dp')
        self.control_layout.add_widget(self.duration_label)
        
        # Load a video
        self.load_video('path_to_your_video.avi')  # Update with your video path

        # Update duration label periodically
        self.bind(size=self.update_duration_label)

        # Back button to return to the footage list view
        self.back_button = Button(text='Back', size_hint=(1, None), height='50dp')
        self.back_button.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_button)

    def load_video(self, filepath):
        if os.path.exists(filepath):
            self.video_player.source = filepath
            self.video_player.state = 'play'  # Start playing the video
            self.play_button.text = 'pause'  # Change button text to Pause
            self.video_player.bind(on_eos=self.on_video_eos)
        else:
            print(f"Video file does not exist: {filepath}")

    def update_progress(self, instance, value):
        # Update the progress bar value
        if self.video.duration > 0:
            self.progress_bar.value = (value / self.video.duration) * 100  # Scale to slider's range
        print(f"Video Position: {value}")

    def update_duration_label(self, *args):
        if self.video_player.state == 'play':
            current_time = self.video_player.position
            duration_time = self.video_player.duration
            self.duration_label.text = f"{self.format_time(current_time)} / {self.format_time(duration_time)}"

    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02}:{seconds:02}"

    def seek_video(self, instance, value):
        if self.video.duration > 0:
            self.video.seek((value / 100) * self.video.duration)

    def rewind_video(self, instance):
        new_position = max(0, self.video_player.position - 10)
        self.video_player.seek(new_position)

    def fast_forward_video(self, instance):
        new_position = min(self.video_player.duration, self.video_player.position + 10)
        self.video_player.seek(new_position)

    def toggle_play(self, instance):
        if self.video_player.state == 'play':
            self.video_player.state = 'pause'
            self.play_button.text = 'play'
        else:
            self.video_player.state = 'play'
            self.play_button.text = 'pause'

    def on_video_eos(self, instance):
        self.play_button.text = 'Play'
        self.video_player.state = 'stop'

    def go_back(self, instance):
        App.get_running_app().root.current = 'ManageFootageScreen'

class VideoPlayerScreen(Screen):
    def __init__(self, **kwargs):
        super(VideoPlayerScreen, self).__init__(**kwargs)

        # Set a responsive size for the app window
        Window.size = (360, 640)  # Might be optional, consider using size_hint

        # Create the CameraFeed component and add it to the screen
        self.video_player = VideoPlayer()
        self.add_widget(self.video_player)

# Class to display and manage footage files
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

        # Bind the on_touch_down event to the FileChooser
        self.filechooser.bind(on_touch_down=self.on_filechooser_touch)

    def on_filechooser_touch(self, instance, touch):
        if instance.collide_point(*touch.pos) and touch.button == 'left':
            # Simulate a file selection
            selection = self.filechooser.selection
            if selection:
                self.go_to_video_player(selection[0])

    def on_select(self, filechooser, selection):
        print("on_select called")
        print(f"Selection: {selection}")  # Print the selection
        
        if selection:
            selected_file = selection[0]
            print(f"Selected file: {selected_file}")  # Print the selected file
            self.go_to_video_player(selected_file)
        else:
            print("No file selected.")

    def go_to_video_player(self, filepath):
        video_player_screen = App.get_running_app().root.get_screen('VideoPlayerScreen')
        video_player_screen.load_video(filepath)  # Load the selected video
        App.get_running_app().root.current = 'VideoPlayerScreen' 
    
    # Method to navigate to the Manage Footage screen
    def go_to_home(self, instance):
        App.get_running_app().root.current = 'MainScreen'

class ManageFootageScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.size = (360, 640)
        self.footage_list = FootageListView()

        self.add_widget(self.footage_list)

class CameraApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='MainScreen'))
        sm.add_widget(CameraScreen(name='CameraScreen'))
        sm.add_widget(ManageFootageScreen(name='ManageFootageScreen'))
        sm.add_widget(ManageFootageScreen(name='PlaceHolder2'))
        sm.add_widget(ManageFootageScreen(name='PlaceHolder3'))
        sm.add_widget(VideoPlayerScreen(name='VideoPlayerScreen'))
        return sm
    
if __name__ == "__main__":
    CameraApp().run()
