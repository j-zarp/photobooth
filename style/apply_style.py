
import cv2
import sys
import os
sys.path.append('/home/jeremie/Downloads/vignettes')
sys.path.append('/home/jeremie/Downloads/vignettes/fast_style_transfer/src')
from fast_style_transfer import evaluate


cam = cv2.VideoCapture('/dev/video0')

style_path = '/home/jeremie/Downloads/vignettes/fast_style_transfer/chkpt_rain'

# Read a frame from the camera
ret,frame = cam.read()

# If the frame was properly read.
if ret is True:
    # Show the captured image and save it
    cv2.imshow('input', frame)
    cv2.imwrite('in/captured.jpg', frame)
    
    # apply style...
    evaluate.main(['--checkpoint', style_path,
               '--in-path', '/home/jeremie/Downloads/vignettes/kivy/style/in',
               '--out-path', '/home/jeremie/Downloads/vignettes/kivy/style/out',
               '--batch-size', '1',
               '--allow-different-dimensions'])
    stylized_img = cv2.imread('/home/jeremie/Downloads/vignettes/kivy/style/out/captured.jpg', cv2.IMREAD_COLOR)
    cv2.imshow('Final', stylized_img)
    cv2.waitKey(0)

cam.release()
cv2.destroyAllWindows()

