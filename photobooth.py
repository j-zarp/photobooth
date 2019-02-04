# coding: utf-8

# Refs kinect:
#   (1) https://github.com/OpenKinect/libfreenect2
#   (2) https://github.com/r9y9/pylibfreenect2

# kivy screens
from kivy.app import App
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, BorderImage # for background
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.lang import Builder
from kivy.properties import OptionProperty

# video
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.clock import Clock, mainthread
import cv2

# mutithreading
# ref: https://stackoverflow.com/questions/26302572/python-kivy-properly-start-a-background-process-that-updates-gui-elements
from threading import Thread

# kinect
from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel

# misc
import os
import sys
import time
import datetime
import subprocess
import numpy as np
from shutil import copyfile
from functools import partial

# fast style transfer
sys.path.append('/home/jeremie/Downloads/vignettes/kivy')
sys.path.append('/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/src')
from fast_style_transfer import evaluate

# windiw parameters
from kivy.core.window import Window
Window.size = (1920, 1080) #(1280, 960)

Builder.load_string("""
<ScreenStart>
    GridLayout:
        size_hint: 1.0, 1.0
        pos_hint: {'center_x': .5, 'center_y': .5}
        rows:1
        canvas.before:
            BorderImage:
                # BorderImage behaves like the CSS BorderImage
                border: 10, 10, 10, 10
                source: 'static/backgrounds/gradient.jpg'
                pos: self.pos
                size: self.size

    Button:
        text: "English"
        font_size: 120
        background_normal: 'static/buttons/normal.png'
        background_down: 'static/buttons/down.png'
        border: 30, 30, 30, 30
        size_hint: .5, .35
        pos_hint: {'center_x': .25, 'center_y': .5}
        on_press: 
            root.set_lang('EN')
            root.manager.current = "screen_selection"

    Button:
        text: "Français"
        font_size: 120
        background_normal: 'static/buttons/normal.png'
        background_down: 'static/buttons/down.png'
        border: 30, 30, 30, 30
        size_hint: .5, .35
        pos_hint: {'center_x': .75, 'center_y': .5}
        on_press: 
            root.set_lang('FR')
            root.manager.current = "screen_selection"

<ScreenSelection>
    Label:
        id: text_id
        text: "Choose a mode"
        font_size: 80
        text_size: self.size
        valign: 'top'
        halign: 'center'
    GridLayout:
        cols: 2
        size_hint_y: .85
        size_hint_x: .85
        pos_hint: {'center_x': .5}
        spacing: [10, 10.]
        Button:
            text: "Empty / Vide"
            font_size: 25
            on_press:
                root.manager.current = "screen_style"
        Button:
            text: "Frame / Cadre"
            font_size: 25
            background_normal: 'static/frames/frame_3.png'
            background_down: 'static/frames/frame_3.png'
            on_press:
                root.manager.current = "screen_frame"
        Button:
            text: "Background / Paysage"
            font_size: 25
            background_normal: 'static/landscapes/matterhorn.jpg'
            background_down: 'static/landscapes/matterhorn.jpg'
            on_press: 
                root.manager.current = "screen_background"
        Button:
            text: "Picture / Tableau"
            font_size: 25
            background_normal: 'static/pictures/dali.jpg'
            background_down: 'static/pictures/dali.jpg'
            on_press: 
                root.manager.current = "screen_picture"

<ScreenPicture>
    Label:
        id: text_id
        text: "Choose a picture"
        font_size: 80
        text_size: self.size
        valign: 'top'
        halign: 'center'
    GridLayout:
        cols: 3
        size_hint_y: .85
        pos_hint: {'center_x': .5, 'center_y': .5}
        spacing: [8, 8.]
        Button:
            text: "Scream"
            font_size: 25
            background_normal: 'static/pictures/scream.jpg'
            background_down: 'static/pictures/scream.jpg'
            on_press:
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/pictures/scream.jpg', True)
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/scream.ckpt')
                root.manager.current = "screen_capture"
        Button:
            text: "Udnie"
            font_size: 25
            background_normal: 'static/pictures/udnie.jpg'
            background_down: 'static/pictures/udnie.jpg'
            on_press:
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/pictures/udnie.jpg', True)
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/udnie.ckpt')
                root.manager.current = "screen_capture"
        Button:
            text: "Dali"
            font_size: 25
            background_normal: 'static/pictures/dali.jpg'
            background_down: 'static/pictures/dali.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/pictures/dali.jpg', True)
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/chkpt_dali')
                root.manager.current = "screen_capture"
        Button:
            text: "Wave"
            font_size: 25
            background_normal: 'static/pictures/wave.jpg'
            background_down: 'static/pictures/wave.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/pictures/wave.jpg', True)
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/wave.ckpt')
                root.manager.current = "screen_capture"
        Button:
            text: "Rain"
            font_size: 25
            background_normal: 'static/pictures/rain.jpg'
            background_down: 'static/pictures/rain.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/pictures/rain.jpg', True)
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/chkpt_rain')
                root.manager.current = "screen_capture"
        Button:
            text: "Muse"
            font_size: 25
            background_normal: 'static/pictures/muse.jpg'
            background_down: 'static/pictures/muse.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/pictures/muse.jpg', True)
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/la_muse.ckpt')
                root.manager.current = "screen_capture"

<ScreenFrame>
    Label:
        id: text_id
        text: "Choose a frame"
        font_size: 80
        text_size: self.size
        valign: 'top'
        halign: 'center'
    GridLayout:
        cols: 3
        size_hint_y: .85
        spacing: [10, 10.]
        Button:
            text: "1"
            font_size: 25
            background_normal: 'static/frames/frame_1.png'
            background_down: 'static/frames/frame_1.png'
            on_press:
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/frames/frame_1.png', True)
                root.manager.current = "screen_style"
        Button:
            text: "2"
            font_size: 25
            background_normal: 'static/frames/frame_2.png'
            background_down: 'static/frames/frame_2.png'
            on_press:
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/frames/frame_2.png', True)
                root.manager.current = "screen_style"
        Button:
            text: "3"
            font_size: 25
            background_normal: 'static/frames/frame_3.png'
            background_down: 'static/frames/frame_3.png'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/frames/frame_3.png', True)
                root.manager.current = "screen_style"
        Button:
            text: "4"
            font_size: 25
            background_normal: 'static/frames/frame_4.png'
            background_down: 'static/frames/frame_4.png'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/frames/frame_4.png', True)
                root.manager.current = "screen_style"
        Button:
            text: "5"
            font_size: 25
            background_normal: 'static/frames/frame_5.png'
            background_down: 'static/frames/frame_5.png'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/frames/frame_5.png', True)
                root.manager.current = "screen_style"
        Button:
            text: "6"
            font_size: 25
            background_normal: 'static/frames/frame_6.png'
            background_down: 'static/frames/frame_6.png'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/frames/frame_6.png', True)
                root.manager.current = "screen_style"

<ScreenBackground>
    Label:
        id: text_id
        text: "Choose a background"
        font_size: 80
        text_size: self.size
        valign: 'top'
        halign: 'center'
    GridLayout:
        cols: 3
        size_hint_y: .85
        size_hint_x: .75
        pos_hint: {'center_x': .5}
        spacing: [8, 8.]
        Button:
            text: "Underwater"
            font_size: 25
            background_normal: 'static/landscapes/underwater.jpg'
            background_down: 'static/landscapes/underwater.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/landscapes/underwater.jpg')
                root.manager.current = "screen_style"
        Button:
            text: "Matterhorn"
            font_size: 25
            background_normal: 'static/landscapes/matterhorn.jpg'
            background_down: 'static/landscapes/matterhorn.jpg'
            on_press:
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/landscapes/matterhorn.jpg')
                root.manager.current = "screen_style"
        Button:
            text: "New York"
            font_size: 25
            background_normal: 'static/landscapes/times_square.jpg'
            background_down: 'static/landscapes/times_square.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/landscapes/times_square.jpg')
                root.manager.current = "screen_style"
        Button:
            text: "Michigan"
            font_size: 25
            background_normal: 'static/landscapes/big_sable.jpg'
            background_down: 'static/landscapes/big_sable.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/landscapes/big_sable.jpg')
                root.manager.current = "screen_style"
        Button:
            text: "Desert"
            font_size: 25
            background_normal: 'static/landscapes/desert.jpg'
            background_down: 'static/landscapes/desert.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/landscapes/desert.jpg')
                root.manager.current = "screen_style"
        Button:
            text: "Moon"
            font_size: 25
            background_normal: 'static/landscapes/moon.jpg'
            background_down: 'static/landscapes/moon.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/landscapes/moon.jpg')
                root.manager.current = "screen_style"
        Button:
            text: "Stage"
            font_size: 25
            background_normal: 'static/landscapes/stage.jpg'
            background_down: 'static/landscapes/stage.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/landscapes/stage.jpg')
                root.manager.current = "screen_style"
        Button:
            text: "Versailles"
            font_size: 25
            background_normal: 'static/landscapes/versailles.jpg'
            background_down: 'static/landscapes/versailles.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/landscapes/versailles.jpg')
                root.manager.current = "screen_style"
        Button:
            text: "Shire"
            font_size: 25
            background_normal: 'static/landscapes/shire.jpg'
            background_down: 'static/landscapes/shire.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('bg_name','static/landscapes/shire.jpg')
                root.manager.current = "screen_style"

<ScreenStyle>
    Label:
        id: text_id
        text: "Choose a style"
        font_size: 80
        text_size: self.size
        valign: 'top'
        halign: 'center'
    GridLayout:
        cols: 3
        size_hint_y: .85
        size_hint_x: .75
        pos_hint: {'center_x': .5}
        spacing: [8, 8.]
        Button:
            text: "None / Aucun"
            font_size: 25
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('style_path','')
                root.manager.current = "screen_capture"
        Button:
            text: "Rain"
            font_size: 25
            background_normal: 'static/styles/rain_princess.jpg'
            background_down: 'static/styles/rain_princess.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/chkpt_rain')
                root.manager.current = "screen_capture"
        Button:
            text: "Manga"
            font_size: 25
            background_normal: 'static/styles/manga.jpg'
            background_down: 'static/styles/maanga.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/chkpt_manga')
                root.manager.current = "screen_capture"
        Button:
            text: "Sketch"
            font_size: 25
            background_normal: 'static/styles/sketch.jpg'
            background_down: 'static/styles/sketch.jpg'
            on_press:
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/chkpt_sketch')
                root.manager.current = "screen_capture"
        Button:
            text: "Udnie"
            font_size: 25
            background_normal: 'static/styles/udnie.jpg'
            background_down: 'static/styles/udnie.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/udnie.ckpt')
                root.manager.current = "screen_capture"
        Button:
            text: "Dali"
            font_size: 25
            background_normal: 'static/styles/dali.jpg'
            background_down: 'static/styles/dali.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/chkpt_dali')
                root.manager.current = "screen_capture"
        Button:
            text: "Scream"
            font_size: 25
            background_normal: 'static/styles/the_scream.jpg'
            background_down: 'static/styles/the_scream.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/scream.ckpt')
                root.manager.current = "screen_capture"
        Button:
            text: "Wave"
            font_size: 25
            background_normal: 'static/styles/wave.jpg'
            background_down: 'static/styles/wave.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/wave.ckpt')
                root.manager.current = "screen_capture"
        Button:
            text: "Muse"
            font_size: 25
            background_normal: 'static/styles/la_muse.jpg'
            background_down: 'static/styles/la_muse.jpg'
            on_press: 
                root.manager.get_screen('screen_capture').save_choice('style_path','/home/jeremie/Downloads/vignettes/kivy/fast_style_transfer/la_muse.ckpt')
                root.manager.current = "screen_capture"

<ScreenCapture>
    KivyCamera:
        id: cam_id
        pos_hint: {'center_x': .5, 'center_y': .5}
    GridLayout:

    Button:
        id: capture_button_id
        text: "Capture"
        font_size: 70
        disabled_color: 1,1,1,1 # white (like when enabled)
        background_normal: 'static/buttons/normal.png'
        background_down: 'static/buttons/down.png'
        background_disabled_normal: 'static/buttons/normal.png'
        background_disabled_down: 'static/buttons/down.png'
        border: 30, 30, 30, 30
        size_hint: .32, .18
        pos_hint: {'center_x': .5, 'bottom_y': .02}
        on_press: root.start_countdown()

<ScreenDisplay>
    Image:
        id: image_area_id
        pos_hint: {'center_x': .5, 'center_y': .5}
        source: 'static/gifs/loading_4.gif.zip'

    GridLayout:
        size_hint: 1.0, 1.0
        pos_hint: {'center_x': .5, 'center_y': .5}
        rows:1

    Button:
        id: btn_print_id
        text: "Print"
        font_size: 70
        background_normal: 'static/buttons/normal.png'
        background_down: 'static/buttons/down.png'
        border: 30, 30, 30, 30
        size_hint: .32, .18
        pos_hint: {'center_x': .25, 'bottom_y': .02}
        on_press: 
            root.print_image()

    Button:
        id: btn_end_id
        text: "End"
        font_size: 70
        background_normal: 'static/buttons/normal.png'
        background_down: 'static/buttons/down.png'
        border: 30, 30, 30, 30
        size_hint: .32, .18
        pos_hint: {'center_x': .75, 'bottom_y': .02}
        on_press: 
            root.manager.transition.direction = "left"
            root.manager.transition.duration = 1
            root.manager.current = "screen_start"
""")

class KivyCamera(Image):
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)

    def setup(self, fn, pipeline, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.bg_image = None
        self.current_img = None
        self.current_mask = None

        serial = fn.getDeviceSerialNumber(0)
        self.device = fn.openDevice(serial, pipeline=pipeline)

        self.listener = SyncMultiFrameListener(
                 FrameType.Color | FrameType.Ir | FrameType.Depth)

        # Register listeners
        self.device.setColorFrameListener(self.listener)
        self.device.setIrAndDepthFrameListener(self.listener)

        self.device.start()

        # NOTE: must be called after device.start()
        self.registration = Registration(self.device.getIrCameraParams(),
                                           self.device.getColorCameraParams())

        self.undistorted = Frame(512, 424, 4)
        self.registered = Frame(512, 424, 4)

        # Optinal parameters for registration
        # set True if you need
        need_bigdepth = True
        need_color_depth_map = False

        self.bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
        self.color_depth_map = np.zeros((424, 512),  np.int32).ravel() \
            if need_color_depth_map else None

        self.clipping_distance = 0.5


    def update(self, dt):
        frames = self.listener.waitForNewFrame()
        color = frames["color"]
        depth = frames["depth"]

        self.registration.apply(color, depth, self.undistorted, self.registered,
                               bigdepth=self.bigdepth,
                               color_depth_map=self.color_depth_map)

        color_img = color.asarray()
        depth_img = self.bigdepth.asarray(np.float32) / 4500. # scale to interval [0,1]

        if(self.bg_image is not None):
            if(self.bg_image.shape[2] == 4): # put frame around picture
                fgMask = self.bg_image[:,:,2]>0
            else: # modify background
                # if needed: denoise filter
                #depth_img = cv2.medianBlur(depth_img, 5)
                #depth_img = cv2.GaussianBlur(depth_img, (9,9), 0)
                fgMask = ((depth_img > self.clipping_distance) & (depth_img > 0))
                fgMask = cv2.resize(fgMask.astype(np.uint8), (1920, 1080))
                
                # if needed: morphological operations
                #kernel = np.ones((10,10), np.uint8)
                #fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_CLOSE, kernel)
                #fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel)
            
            fgMask_3d = np.dstack((fgMask, fgMask, fgMask)).astype(np.bool) # mask is 1 channel, color is 3 channels
            final_img = np.where(fgMask_3d, self.bg_image[:,:,:3], color_img[:,:,:3])
        else:
            fgMask_3d = None
            final_img = color_img[:,:,:3]

        self.listener.release(frames)

        self.current_img = final_img
        self.current_mask = fgMask_3d
        self.display_img(final_img)

    def display_img(self, img):
        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgb') #(480,640)
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.texture = image_texture


class ScreenStart(Screen):
    def __init__(self, **kwargs):
        super(ScreenStart, self).__init__(**kwargs)

    def on_pre_enter(self):
        screenmanager.transition = SlideTransition(direction="left", duration=1)

    def set_lang(self, lang):
        screenmanager.language = lang


class ScreenSelection(Screen):
    def __init__(self, **kwargs):
        super(ScreenSelection, self).__init__(**kwargs)
    def on_pre_enter(self):
        if(screenmanager.language == 'EN'):
            self.ids.text_id.text = 'Choose a mode'
        else:
            self.ids.text_id.text = 'Choisissez un mode'

class ScreenPicture(Screen):
    def __init__(self, **kwargs):
        super(ScreenPicture, self).__init__(**kwargs)
    def on_pre_enter(self):
        if(screenmanager.language == 'EN'):
            self.ids.text_id.text = 'Choose a Picture'
        else:
            self.ids.text_id.text = 'Choisissez un tableau'

class ScreenFrame(Screen):
    def __init__(self, **kwargs):
        super(ScreenFrame, self).__init__(**kwargs)
    def on_pre_enter(self):
        if(screenmanager.language == 'EN'):
            self.ids.text_id.text = 'Choose a frame'
        else:
            self.ids.text_id.text = 'Choisissez un cadre'

class ScreenBackground(Screen):
    def __init__(self, **kwargs):
        super(ScreenBackground, self).__init__(**kwargs)
    def on_pre_enter(self):
        if(screenmanager.language == 'EN'):
            self.ids.text_id.text = 'Choose a background'
        else:
            self.ids.text_id.text = 'Choisissez un fond'

class ScreenStyle(Screen):
    def __init__(self, **kwargs):
        super(ScreenStyle, self).__init__(**kwargs)
    def on_pre_enter(self):
        if(screenmanager.language == 'EN'):
            self.ids.text_id.text = 'Choose a style'
        else:
            self.ids.text_id.text = 'Choisissez un style'

class ScreenCapture(Screen):
    def __init__(self, fn, pipeline, img_size, **kwargs):
        super(ScreenCapture, self).__init__(**kwargs)
        self.bg_name = None
        self.style_path = None
        self.img_fname = None
        self.img_size = img_size
        self.ids.cam_id.setup(fn=fn, pipeline=pipeline)
        self.counter = 0

    def on_pre_enter(self):
        Clock.schedule_interval(self.ids.cam_id.update, 1.0 / 20) # for 20 fps

    def on_leave(self):
        # restore capture button
        self.ids.capture_button_id.text = 'Capture'
        self.ids.capture_button_id.disabled = False

    def save_choice(self, name, value, keep_unchanged=False):
        setattr(self, name, value)
        if(name=='bg_name'):
            bg_image = cv2.imread(self.bg_name, cv2.IMREAD_UNCHANGED)
            bg_image = cv2.resize(bg_image, self.img_size)
            self.ids.cam_id.bg_image = bg_image
            if(keep_unchanged):
                screenmanager.get_screen('screen_display').orig_background = bg_image


    def start_countdown(self):
        # prevent the user to click several times
        self.ids.capture_button_id.disabled = True
        self.counter = 0
        Clock.schedule_interval(self.wait_and_capture, 1)

    def go_to_display_screen(self, *args):
        self.ids.cam_id.bg_name = None
        self.ids.cam_id.bg_image = None
        screenmanager.transition = NoTransition()
        screenmanager.current = 'screen_display'

    def wait_and_capture(self, *args):
        self.ids.capture_button_id.text = str(5-self.counter)
        self.counter += 1
        if(self.counter>5):
            self.ids.capture_button_id.text = 'cheese!'
            self.counter = 0
            Clock.unschedule(self.wait_and_capture)

            # freeze webcam input
            Clock.unschedule(self.ids.cam_id.update)

            # save image
            now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%s')
            self.img_fname = 'captured_' + now + '.jpg'
            cv2.imwrite(os.path.join('static/in',self.img_fname), self.ids.cam_id.current_img)

            # set filename to None (not ready) for the display screen and pass mask
            screenmanager.get_screen('screen_display').img_fname = None
            screenmanager.get_screen('screen_display').img_mask = self.ids.cam_id.current_mask

            if(not self.style_path): # no defined style to be applied
                copyfile(os.path.join('static/in',self.img_fname), os.path.join('static/out',self.img_fname))
                os.remove(os.path.join('static/in',self.img_fname))
                # update filename for the display screen
                screenmanager.get_screen('screen_display').img_fname = self.img_fname
                Clock.schedule_once(self.go_to_display_screen, 2)
            else:
                self.go_to_display_screen()
                Thread(target=self.apply_style).start() # launch on new thread


    def apply_style(self):
        ## DEBUG ##
        #copyfile(os.path.join('static/in',self.img_fname), os.path.join('static/out',self.img_fname))
        #time.sleep(10)
        ## ----- ##
        evaluate.main(['--checkpoint', self.style_path,
                       '--in-path', 'static/in',
                       '--out-path', 'static/out',
                       '--batch-size', '1',
                       '--allow-different-dimensions'])
        os.remove(os.path.join('static/in', self.img_fname))
        # update filename for the display screen
        screenmanager.get_screen('screen_display').img_fname = self.img_fname



class ScreenDisplay(Screen):
    def __init__(self, **kwargs):
        super(ScreenDisplay, self).__init__(**kwargs)
        self.img_fname = None
        self.img_mask = None
        self.orig_background = None

    def on_pre_enter(self):
        self.ids.image_area_id.source = 'static/gifs/loading_4.gif'
        self.ids.image_area_id.anim_delay = 1./30
        Clock.schedule_interval(self.update_background, 0.2)
        if(screenmanager.language == 'EN'):
            self.ids.btn_end_id.text = 'End'
            self.ids.btn_print_id.text = 'Print'
        else:
            self.ids.btn_end_id.text = 'Fin'
            self.ids.btn_print_id.text = 'Imprimer'

    def update_background(self, dt):
        if(self.img_fname is not None):
            Clock.unschedule(self.update_background)
            img_full_path = os.path.join('static/out',self.img_fname)
            if(self.orig_background is not None): # in the case where we need to restore the original background
              img = cv2.imread(img_full_path, cv2.IMREAD_UNCHANGED)
              img = np.where(self.img_mask, self.orig_background[:,:,:3], img[:,:,:3])
              cv2.imwrite(img_full_path, img)
            self.ids.image_area_id.source = img_full_path
            self.orig_background = None

    def print_image(self):
        pass
        #TODO check behavior with real printer
        # img_full_path = os.path.join('static/out',self.img_fname)
        # bashCommand = "lp " + img_full_path
        # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        # output, error = process.communicate()
        # print('output:', output)
        # print('error:', error)


class ScreenManagerLang(ScreenManager):

    language = OptionProperty('EN', options=('EN', 'FR'))

    def __init__(self, **kwargs):
        super(ScreenManagerLang, self).__init__(**kwargs)


class MainApp(App):
    def build(self):
        self.root = screenmanager
        return self.root

    def on_stop(self):
        screenmanager.get_screen('screen_capture').ids.cam_id.device.stop()
        screenmanager.get_screen('screen_capture').ids.cam_id.device.close()

if __name__ == '__main__':
    from pylibfreenect2 import OpenCLPacketPipeline
    pipeline = OpenCLPacketPipeline()
    print("Packet pipeline:", type(pipeline).__name__)

    # Create and set logger
    logger = createConsoleLogger(LoggerLevel.Warning) #(LoggerLevel.Debug)
    setGlobalLogger(logger)

    fn = Freenect2()
    num_devices = fn.enumerateDevices()
    if num_devices == 0:
        print("No device connected!")
        sys.exit(1)

    screenmanager = ScreenManagerLang()
    screenmanager.add_widget(ScreenStart(name="screen_start"))
    screenmanager.add_widget(ScreenSelection(name="screen_selection"))
    screenmanager.add_widget(ScreenPicture(name="screen_picture"))
    screenmanager.add_widget(ScreenFrame(name="screen_frame"))
    screenmanager.add_widget(ScreenBackground(name="screen_background"))
    screenmanager.add_widget(ScreenStyle(name="screen_style"))
    screenmanager.add_widget(ScreenCapture(name="screen_capture", fn=fn, pipeline=pipeline, img_size=Window.size)) # screen size: 1920 x 1080
    screenmanager.add_widget(ScreenDisplay(name="screen_display"))

    MainApp().run()

