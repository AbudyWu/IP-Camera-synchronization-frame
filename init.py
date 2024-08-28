import os
import cv2
import datetime
from time import sleep
import numpy as np
from threading import Thread

# out = cv2.VideoWriter(os.path.join(save_dir1, f'{latest_number1:03d}-1.mp4'), fourcc, FPS, (synced_frame1.shape[1], synced_frame1.shape[0]))

def newname(save_dir):
    existing_files = os.listdir(save_dir)
    existing_files = [f for f in existing_files if f.endswith('.mp4')]
    if existing_files:
        existing_files.sort()
        latest_file = existing_files[-1]
        latest_number = int(latest_file.split('-')[0])
        return latest_number + 1
    else:
        return 1

def save2(save_dir):
    save_dir1 = os.path.join(save_dir, 'camera108')
    save_dir2 = os.path.join(save_dir, 'camera109')

    os.makedirs(save_dir1, exist_ok=True)
    os.makedirs(save_dir2, exist_ok=True)

    latest_number1 = newname(save_dir1)
    latest_number2 = newname(save_dir2)

    return latest_number1, latest_number2, save_dir1, save_dir2

class RTSPThread(Thread):
    '''
    The RTSPThread class captures frames from a video stream and displays them in a window, with the
    option to save frames as images or quit the window.
    '''

    def __init__(self, cam: cv2.VideoCapture, window_name: str):
        '''
        This function initializes a thread for capturing video frames from a camera.

        Args:
            `cam` (cv2.VideoCapture): An instance of the cv2.VideoCapture class, which is used to capture video
            from a camera or a video file. It is passed to the constructor of the class as an argument.
        '''
        # execute the base constructor
        Thread.__init__(self)
        # set a default value
        self.cam = cam
        self.window_name = window_name
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        self.frame: np.ndarray = None
        self.ret: bool = False
        self.showWindow = False
        self.daemon = True
        self.isActive = True
        self.start()

    def run(self) -> None:
        '''
        This function continuously reads frames from a camera and sets a sleep time of 1/30 seconds between
        each frame.
        '''
        while self.isActive:
            self.ret, self.frame = self.cam.read()
            sleep(1 / (15 * 2))

    def imshow(self):
        '''
        This function displays a video stream and allows the user to save frames or quit the window.

        Returns:
            a boolean value. If the user presses the 'q' key, the function returns False, otherwise it
            continues to run.
        '''
        if self.showWindow is False:
            self.showWindow = True
            cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        if self.ret:
            cv2.imshow(self.window_name, cv2.resize(self.frame, (720, 480)))
            key_signal = cv2.waitKey(1)

            # if key_signal == ord(' '):
            #     cv2.imwrite(f'{out}/{datetime.timestamp(datetime.now())}.png', self.frame)
            if key_signal == ord('q'):
                return False
            
        return True
