from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2
import numpy as np

class UFOApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Camera
        self.image = Image()
        self.add_widget(self.image)
        
        # Status
        self.status = Label(text="READY", size_hint=(1, 0.1))
        self.add_widget(self.status)
        
        # Buttons
        btn_layout = BoxLayout(size_hint=(1, 0.1))
        self.btn_capture = Button(text="CAPTURE")
        self.btn_capture.bind(on_press=self.capture_target)
        btn_layout.add_widget(self.btn_capture)
        
        self.btn_unlock = Button(text="UNLOCK")
        self.btn_unlock.bind(on_press=self.unlock_target)
        btn_layout.add_widget(self.btn_unlock)
        self.add_widget(btn_layout)
        
        # Camera
        self.camera = None
        self.target_locked = False
        self.prev_gray = None
        self.threshold = 30
        self.start_camera()
    
    def start_camera(self):
        try:
            from kivy.uix.camera import Camera
            self.camera = Camera(resolution=(640, 480), play=True)
            self.camera.bind(on_tex=self.on_frame)
            self.add_widget(self.camera)
            self.remove_widget(self.image)
            self.add_widget(self.image)
            Clock.schedule_interval(self.update, 1.0/30.0)
        except:
            self.status.text = "Camera failed"
    
    def on_frame(self, *args):
        if self.camera is None or self.camera._camera is None:
            return
        if self.camera._camera._buffer is None:
            return
        
        try:
            w = self.camera.resolution[0]
            h = self.camera.resolution[1]
            buf = self.camera._camera._buffer.tostring()
            img = np.frombuffer(buf, np.uint8)
            img = img.reshape((h * 3 // 2, w))
            frame = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_NV21)
            
            # Motion detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if self.prev_gray is not None:
                diff = cv2.absdiff(self.prev_gray, gray)
                _, thresh = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    if cv2.contourArea(cnt) > 500:
                        x, y, w2, h2 = cv2.boundingRect(cnt)
                        cv2.rectangle(frame, (x, y), (x+w2, y+h2), (0, 255, 0), 2)
            self.prev_gray = gray
            
            # Display
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            texture = Texture.create(size=(rgb.shape[1], rgb.shape[0]), colorfmt='rgb')
            texture.blit_buffer(rgb.tostring(), colorfmt='rgb', bufferfmt='ubyte')
            self.image.texture = texture
            
        except Exception as e:
            pass
    
    def capture_target(self, instance):
        self.status.text = "CAPTURE ARMED"
        self.target_locked = True
    
    def unlock_target(self, instance):
        self.target_locked = False
        self.status.text = "UNLOCKED"
    
    def update(self, dt):
        pass

class MainApp(App):
    def build(self):
        return UFOApp()

if __name__ == '__main__':
    MainApp().run()
