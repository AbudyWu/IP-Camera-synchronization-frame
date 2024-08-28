import cv2
import threading
import time
import collections
import os

FPS = 30
save_dir = 'Dataset_0826'

buffer1 = collections.deque(maxlen=60)
buffer2 = collections.deque(maxlen=60)
buffer3 = collections.deque(maxlen=60)

str1 = "rtsp://admin:sp123456@192.168.1.108/"
str2 = "rtsp://admin:sp123456@192.168.1.109/"

cap1 = cv2.VideoCapture(str1)
cap2 = cv2.VideoCapture(str2)

buffer_lock = threading.Lock()
running = True  

def capture_camera_1():
    global running
    while running:
        ret, frame = cap1.read()
        if ret:
            timestamp = time.time()
            with buffer_lock:
                buffer1.append((frame, timestamp))
            # print("108 time =", timestamp)
        else:
            print("Reconnecting to camera 1...")
            cap1.release()
            cap1.open(str1)

def capture_camera_2():
    global running
    while running:
        ret, frame = cap2.read()
        if ret:
            timestamp = time.time()
            with buffer_lock:
                buffer2.append((frame, timestamp))
            # print("109 time =", timestamp)
        else:
            print("Reconnecting to camera 2...")
            cap2.release()
            cap2.open(str2)

thread1 = threading.Thread(target=capture_camera_1)
thread2 = threading.Thread(target=capture_camera_2)
thread1.start()
thread2.start()

def find_best_match(buffer1, buffer2):
    min_diff = float('inf')
    best_match = None
    
    for i, (frame1, timestamp1) in enumerate(buffer1):
        for j, (frame2, timestamp2) in enumerate(buffer2):
            diff = abs(timestamp1 - timestamp2)
            if diff < min_diff:
                min_diff = diff
                best_match = (i, j, frame1, frame2, timestamp1, timestamp2)
    
    return best_match


save_dir1 = os.path.join(save_dir, 'camera108')
save_dir2 = os.path.join(save_dir, 'camera109')

os.makedirs(save_dir1, exist_ok=True)
os.makedirs(save_dir2, exist_ok=True)

existing_files1 = os.listdir(save_dir1)
existing_files1 = [f for f in existing_files1 if f.endswith('.mp4')]
if existing_files1:
    existing_files1.sort()
    latest_file1 = existing_files1[-1]
    latest_number1 = int(latest_file1.split('-')[0])
else:
    latest_number1 = 0

existing_files2 = os.listdir(save_dir2)
existing_files2 = [f for f in existing_files2 if f.endswith('.mp4')]
if existing_files2:
    existing_files2.sort()
    latest_file2 = existing_files2[-1]
    latest_number2 = int(latest_file2.split('-')[0])
else:
    latest_number2 = 0

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

out1 = None
out2 = None

last_timestamp1 = None
last_timestamp2 = None
recording = False
try:
    while True:
        with buffer_lock:
            if buffer1 and buffer2:
                match = find_best_match(buffer1, buffer2)
                if match:
                    i, j, frame1, frame2, timestamp1, timestamp2 = match
                    buffer3.append((frame1, frame2, timestamp1, timestamp2))

                    while buffer1 and buffer1[0][1] <= timestamp1:
                        buffer1.popleft()
                    while buffer2 and buffer2[0][1] <= timestamp2:
                        buffer2.popleft()

                    # print(f"Synced frames at time {timestamp1} and {timestamp2}, diff = {abs(timestamp1 - timestamp2)}")
            
        if buffer3:
            synced_frame1, synced_frame2, timestamp1, timestamp2 = buffer3.popleft()

            resized_frame1 = cv2.resize(synced_frame1, (0, 0), fx=0.5, fy=0.5)
            resized_frame2 = cv2.resize(synced_frame2, (0, 0), fx=0.5, fy=0.5)

            combined_frame = cv2.hconcat([resized_frame1, resized_frame2])

            cv2.imshow('Synchronized Frames', combined_frame)

            # if recording == True:
            if out1 is None:
                latest_number1 += 1
                out1 = cv2.VideoWriter(os.path.join(save_dir1, f'{latest_number1:03d}-1.mp4'), fourcc, FPS, (synced_frame1.shape[1], synced_frame1.shape[0]))
            
            if out2 is None:
                latest_number2 += 1
                out2 = cv2.VideoWriter(os.path.join(save_dir2, f'{latest_number2:03d}-2.mp4'), fourcc, FPS, (synced_frame2.shape[1], synced_frame2.shape[0]))

            if last_timestamp1 is not None and last_timestamp2 is not None:
                time_diff1 = timestamp1 - last_timestamp1
                time_diff2 = timestamp2 - last_timestamp2
                
                frame_interval1 = max(1, int(FPS * time_diff1))
                frame_interval2 = max(1, int(FPS * time_diff2))
                
                for _ in range(frame_interval1):
                    out1.write(synced_frame1)
                for _ in range(frame_interval2):
                    out2.write(synced_frame2)
            
            last_timestamp1 = timestamp1
            last_timestamp2 = timestamp2

        # key = cv2.waitKey(1) & 0xFF
        # if key == ord(' '):
        #     recording = not recording
        #     print(f"Recording = {recording}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    running = False
    thread1.join()
    thread2.join()
    cap1.release()
    cap2.release()
    if out1:
        out1.release()
    if out2:
        out2.release()
    cv2.destroyAllWindows()
