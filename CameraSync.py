import cv2
import time
import threading
from threading import Thread
from time import sleep
from queue import Queue


class CameraSyncThread(Thread):
    def __init__(self, cam1_url: str, cam2_url: str, max_queue_size=2):
        super().__init__()
        self.cap1 = cv2.VideoCapture(cam1_url)
        self.cap2 = cv2.VideoCapture(cam2_url)
        self.max_queue_size = max_queue_size
        self.q1 = Queue(maxsize=self.max_queue_size)
        self.q2 = Queue(maxsize=self.max_queue_size)
        self.frame1 = None
        self.frame2 = None
        self.isActive = True
        self._initialize_cameras()
        self.start()

    def _initialize_cameras(self):
        self.cap1.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        self.cap2.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        threading.Thread(target=self.__get_frame, args=(self.q1, self.cap1)).start()
        threading.Thread(target=self.__get_frame, args=(self.q2, self.cap2)).start()

    def __synchronize_queues(self, q):
        latest = min(self.q1.qsize(), self.q2.qsize())
        while q.qsize() > latest:
            q.get()

    def __get_frame(self, q, cap):
        while self.isActive:
            ret, frame = cap.read()
            if ret:
                self.__synchronize_queues(q)
                if q.qsize() < self.max_queue_size:
                    q.put(frame)
        # sleep(1 / (15 * 2))

    def update_frames(self):
        if not self.q1.empty() and not self.q2.empty():
            self.frame1 = self.q1.get()
            self.frame2 = self.q2.get()
        else:
            self.frame1, self.frame2 = None, None

    def get_frames(self):
        return self.frame1, self.frame2

    def run(self):
        while self.isActive:
            start_time = time.time()
            self.update_frames()
            elapsed_time = time.time() - start_time
            sleep_time = max(0, (1 / 30) - elapsed_time)
            time.sleep(sleep_time)

    def release(self):
        self.isActive = False
        self.cap1.release()
        self.cap2.release()


if __name__ == "__main__":
    str1 = "rtsp://admin:sp123456@192.168.1.108/"
    str2 = "rtsp://admin:sp123456@192.168.1.109/"
    camera_sync = CameraSyncThread(str1, str2)

    while True:
        frame108, frame109 = camera_sync.get_frames()
        if frame108 is not None and frame109 is not None:
            resized_frame108 = cv2.resize(frame108, (0, 0), fx=0.5, fy=0.5)
            resized_frame109 = cv2.resize(frame109, (0, 0), fx=0.5, fy=0.5)
            combined_frame = cv2.hconcat([resized_frame108, resized_frame109])
            cv2.imshow("Combined Frame", combined_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    camera_sync.release()
    cv2.destroyAllWindows()
