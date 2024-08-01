import cv2
import threading
import numpy as np
import os
from queue import Queue

str1 = "rtsp://admin:sp123456@192.168.1.108/"
str2 = "rtsp://admin:sp123456@192.168.1.109/"

cap1 = cv2.VideoCapture(str1)
cap2 = cv2.VideoCapture(str2)

maxsize = 1  
q1 = Queue(maxsize=maxsize)
q2 = Queue(maxsize=maxsize)

output_dir = "./69/"
os.makedirs(output_dir, exist_ok=True)

def syn_time(q):
    latest = min(q1.qsize(), q2.qsize())
    if latest and q.qsize() > latest:
        for _ in range(q.qsize() - latest):
            q.get()

def get_frame(q, cap):
    while True:
        ret, frame = cap.read()
        if ret:
            syn_time(q)
            if q.qsize() < maxsize:
                q.put(frame)

def save_images(frame1, frame2, count):
    imname1 = f"{output_dir}img108_{count}.png"
    imname2 = f"{output_dir}img109_{count}.png"
    cv2.imwrite(imname1, frame1)
    cv2.imwrite(imname2, frame2)
    print(f"儲存影像: {imname1} 和 {imname2}")

def process_frames():
    count = 0

    while True:
        if not q1.empty() and not q2.empty():
            frame1 = q1.get()
            frame2 = q2.get()

            # 顯示即時影像
            resized_frame1 = cv2.resize(frame1, (0, 0), fx=0.5, fy=0.5)
            resized_frame2 = cv2.resize(frame2, (0, 0), fx=0.5, fy=0.5)

            combined_frame = cv2.hconcat([resized_frame1, resized_frame2])

            cv2.imshow('Synchronized Frames', combined_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                count += 1
                save_images(frame1, frame2, count)
                cv2.waitKey(500)
            elif key == ord('q'):  
                break

    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()

thread1 = threading.Thread(target=get_frame, args=(q1, cap1)).start()
thread2 = threading.Thread(target=get_frame, args=(q2, cap2)).start()

process_frames()
