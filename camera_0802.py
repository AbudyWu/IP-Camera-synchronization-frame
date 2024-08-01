import cv2
import os
import time
import threading
from queue import Queue
from init import save2

FPS = 30
save_dir = './output'  # 替換成你保存文件的目錄

str1 = "rtsp://admin:sp123456@192.168.1.108/"
str2 = "rtsp://admin:sp123456@192.168.1.109/"

cap1 = cv2.VideoCapture(str1)
cap2 = cv2.VideoCapture(str2)

maxsize = 1 # 調整佇列大小
q1 = Queue(maxsize=maxsize)
q2 = Queue(maxsize=maxsize)

def syn_time(q1, q2):
    latest = min(q1.qsize(), q2.qsize())
    if latest:
        while q1.qsize() > latest:
            q1.get()
        while q2.qsize() > latest:
            q2.get()

def get_frame(q, cap):
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                raise Exception("Failed to capture frame")
            if q.qsize() < maxsize:
                q.put(frame)
        except Exception as e:
            print(f"Error capturing frame: {e}")
            cap.release()
            cap = cv2.VideoCapture(str1 if q == q1 else str2)
            time.sleep(1)

def write_mp4(frame1, frame2, out1, out2):
    out1.write(frame1)
    out2.write(frame2)

last_num1, last_num2 = save2(save_dir)
save_dir1 = os.path.join(save_dir, 'camera108')
save_dir2 = os.path.join(save_dir, 'camera109')

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out1 = cv2.VideoWriter(os.path.join(save_dir1, f'{last_num1:03d}-1.mp4'), fourcc, FPS, (1920, 1080))
out2 = cv2.VideoWriter(os.path.join(save_dir2, f'{last_num2:03d}-2.mp4'), fourcc, FPS, (1920, 1080))

# Start threads for capturing frames from both cameras
thread1 = threading.Thread(target=get_frame, args=(q1, cap1)).start()
thread2 = threading.Thread(target=get_frame, args=(q2, cap2)).start()

# start_time = time.time()
# frame_count = 0

# Main loop to display synchronized frames
while True:
    if not q1.empty() and not q2.empty():
        frame1 = q1.get()
        frame2 = q2.get()

        # Synchronize frames
        syn_time(q1, q2)

        # Write synchronized frames to MP4 files
        write_mp4(frame1, frame2, out1, out2)

        # frame_count += 1
        # elapsed_time = time.time() - start_time
        # if elapsed_time >= 1.0:
        #     fps = frame_count / elapsed_time
        #     print(f"Recording FPS: {fps:.2f}")
        #     start_time = time.time()
        #     frame_count = 0

        # Resize frames to fit side by side
        resized_frame1 = cv2.resize(frame1, (0, 0), fx=0.5, fy=0.5)
        resized_frame2 = cv2.resize(frame2, (0, 0), fx=0.5, fy=0.5)
        combined_frame = cv2.hconcat([resized_frame1, resized_frame2])

        # Display the combined frame
        cv2.imshow('Combined Frame', combined_frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap1.release()
cap2.release()
# out1.release()
# out2.release()
if out1:
    out1.release()
if out2:
    out2.release()
cv2.destroyAllWindows()
