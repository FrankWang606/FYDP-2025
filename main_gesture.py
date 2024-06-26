import sys
import serial
from collections import deque
import threading
import time
import keyboard  # 导入 keyboard 库
from mpudata import MPUData
import rec_algorithm as Recognizer 


lock = threading.Lock()
# pause_event = threading.Event()

current_gesture = -1 # 0 thumb up, 1 thumb down, 2 wave, 3 pinch in, 4 palm flip, 5 self record
# 设置串口参数
ser = serial.Serial('COM3', 9600)  # 根据实际情况更改 COM 端口

# 创建三个双端队列
mpu0_queue = deque(maxlen=15)
mpu1_queue = deque(maxlen=15)
mpu2_queue = deque(maxlen=15)
# 定义一个标志位用于控制线程的运行
running = True

def parse_data(data):
    parts = data.split(',')
    if len(parts) == 7:
        mpu_name = parts[0]
        ax, ay, az = float(parts[1]), float(parts[2]), float(parts[3])
        rx, ry, rz = float(parts[4]), float(parts[5]), float(parts[6])
        return mpu_name, MPUData(ax, ay, az, rx, ry, rz)
    return None, None

# 读取串口数据的函数
def read_data():
    global running
    while running:
        if ser.in_waiting > 0:
            try:
                data = ser.readline().decode('utf-8').strip()
            except UnicodeDecodeError:
                continue
            mpu_name, mpu_data = parse_data(data)
            if mpu_name == "MPU0":
                mpu0_queue.append(mpu_data)
            elif mpu_name == "MPU1":
                mpu1_queue.append(mpu_data)
            elif mpu_name == "MPU2":
                mpu2_queue.append(mpu_data)


# recognizers
def ges_thumb_up():
    global current_gesture,running
    while running:
        time.sleep(0.05)
        mpu0 = mpu0_queue
        mpu1 = mpu1_queue
        
        if len(mpu0) <= 5 or len(mpu1) <= 5:
            continue
        if(Recognizer.thumb_up(mpu0,mpu1)):
            with lock:
                current_gesture = 0
            time.sleep(3)
            
def ges_thumb_down():
    global current_gesture,running
    while running:
        time.sleep(0.05)
        mpu0 = mpu0_queue
        mpu1 = mpu1_queue
        
        if len(mpu0) <= 5 or len(mpu1) <= 5:
            continue
        if(Recognizer.thumb_down(mpu0,mpu1)):
            with lock:
                current_gesture = 1
            time.sleep(3)

def ges_wave():
    global current_gesture,running
    while running:
        time.sleep(0.05)
        mpu0 = mpu0_queue
        mpu2 = mpu2_queue
        
        if len(mpu0) < 15 or len(mpu2) < 15:
            continue
        if(Recognizer.wave(mpu0,mpu2)):
            with lock:
                current_gesture = 2
            time.sleep(3)

def ges_pinch():
    global current_gesture,running
    while running:
        time.sleep(0.03)
        mpu0 = mpu0_queue
        mpu1 = mpu1_queue
        
        if len(mpu0) < 15 or len(mpu1) < 15:
            continue
        if(Recognizer.pinch(mpu0,mpu1)):
            with lock:
                current_gesture = 3
            time.sleep(3)

def ges_flip():
    global current_gesture,running
    while running:
        time.sleep(0.05)
        mpu0 = mpu0_queue
        mpu1 = mpu1_queue
        mpu2 = mpu2_queue
        if len(mpu0) < 15 or len(mpu1) < 15 or len(mpu2) < 15:
            continue
        if(Recognizer.flip(mpu0,mpu1,mpu2)):
            with lock:
                current_gesture = 4
            time.sleep(3)

def set_running_false():
    global running
    running = False
    
def current_state_print(state):
    with open('gesture.txt', 'w') as f:
        f.write(str(state))

if __name__ == "__main__":
    keyboard.add_hotkey('q', lambda: set_running_false())
    # 启动一个线程读取串口数据
    thread = threading.Thread(target=read_data)
    thread.start()

    # recognizers
    ges1 = threading.Thread(target=ges_thumb_up)
    ges1.start()
    ges2 = threading.Thread(target=ges_thumb_down)
    ges2.start()
    ges3 = threading.Thread(target=ges_wave)
    ges3.start()   
    ges4 = threading.Thread(target=ges_pinch)
    ges4.start() 
    ges5 = threading.Thread(target=ges_flip)
    ges5.start() 

    while running:
        current_state_print(current_gesture)
        if(current_gesture != -1):
            current_gesture = -1
            time.sleep(2.5)
            continue
        time.sleep(0.5)

    # 等待其他线程结束
    thread.join()
    ges1.join()
    ges2.join()
    ges3.join()
    ges4.join()
    ges5.join()
    ser.close()

    print("Program terminated.")
    sys.exit(0)