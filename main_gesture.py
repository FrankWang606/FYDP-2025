import serial
from collections import deque
import threading
import time
import keyboard  # 导入 keyboard 库
from mpudata import MPUData
import rec_algorithm as Recognizer 


lock = threading.Lock()
# pause_event = threading.Event()

current_gesture = -1
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

def thumb_up():
    if len(mpu0_queue) <= 5 or len(mpu1_queue) <= 5:
        return False
    # pause_event.wait()
    dt0 = mpu0_queue
    dt1 = mpu1_queue
    res = True
    for i in range(-4,0):
        if dt0[i].ax >=7 and dt1[i].ay<=-8 and dt1[i].az<=-3:
            continue
        else:
            res = False
            break
    return res

# 打印队列内容的函数，用于测试
def ges_thumb_up():
    global current_gesture,running
    while running:
        if len(mpu1_queue) == 0:
            continue
        data = mpu1_queue[-1]
        data.printself()
        if(thumb_up()):
            with lock:
                current_gesture = 0
            time.sleep(3)

# 监听组合键的函数
def listen_for_exit():
    global running
    keyboard.add_hotkey('q', lambda: set_running_false())

def set_running_false():
    global running
    running = False
    
def current_state_print(state):
    if state == -1:
        print("no gesture detected")
    if state == 0:
        print("thumb up")
    elif state == 1:
        print("thumb down")
    elif state == 2:
        print("wave")
    elif state == 3:
        print("pinch in")
    elif state == 4:
        print("palm flip")
    elif state == 5:
        print("SELFDEFINED") 

if __name__ == "__main__":
    # 启动一个线程读取串口数据
    thread = threading.Thread(target=read_data)
    thread.start()

    # recognizers
    ges1 = threading.Thread(target=ges_thumb_up)
    ges1.start()

    # 主线程监听组合键
    listen_for_exit()

    while running:
        current_state_print(current_gesture)
        if(current_gesture != -1):
            current_gesture = -1
            time.sleep(3)
            continue
        time.sleep(0.2)

    # 等待其他线程结束
    thread.join()
    ges1.join()
    ser.close()

    print("Program terminated.")