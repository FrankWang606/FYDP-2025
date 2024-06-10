import serial
from collections import deque
import threading
import time
import keyboard  
from mpudata import MPUData 

lock = threading.Lock()
current_gesture = -1
# 创建一个事件对象，用于控制手势识别线程的暂停和继续
pause_event = threading.Event()
# 设置串口
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


# 监听组合键的函数
def listen_for_exit():
    global running
    keyboard.add_hotkey('q', lambda: set_running_false())
    
def thumb_up():
    global running, current_gesture
    res = False
    while running:
        if len(mpu0_queue) <= 5:
            continue
        # pause_event.wait()
        dt = mpu0_queue[-1]
        dt.printself()
        res = True
        for i in range(-3,0):
            j=-1
            # if mpu0_queue[i].ax >=7 and mpu1_queue[i].ay<=-9 and mpu1_queue[i].az<=-4:
            if mpu0_queue[j].ax >=7:
                j-=1
                continue
            else:
                res = False
                break
        if res:
            with lock:
                if current_gesture == -1:
                    current_gesture = 0
            
    
def gesture_recognizer():
    global running, current_gesture
    while running:
        if current_gesture != -1:
            if current_gesture == 0:
                print("thumb up")
            elif current_gesture == 1:
                print("thumb down")
            elif current_gesture == 2:
                print("wave")
            elif current_gesture == 3:
                print("pinch in")
            elif current_gesture == 4:
                print("palm flip")
            elif current_gesture == 5:
                print("SELFDEFINED") 
                
            pause_event.clear()
            time.sleep(3)
            current_gesture = -1
            pause_event.set()   
        

def set_running_false():
    global running
    running = False

if __name__ == "__main__":
    pause_event.set()
    # 启动一个线程读取串口数据
    thread = threading.Thread(target=read_data)
    thread.start()

    # 启动多线程手势识别
    ges1 = threading.Thread(target=thumb_up)
    ges1.start()
    # 启动一个线程输出手势识别结果
    rec_thread = threading.Thread(target=gesture_recognizer)
    rec_thread.start()


    listen_for_exit()

    while running:
        time.sleep(0.1)  # 让主线程保持运行状态


    thread.join()
    rec_thread.join()
    ges1.join()
    ser.close()

    print("Program terminated.")