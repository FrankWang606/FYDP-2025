import serial
from collections import deque
import threading
import time
import keyboard  # 导入 keyboard 库
from mpudata import MPUData 

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

# 打印队列内容的函数，用于测试
def print_queues():
    global running
    while running:
        print("MPU0 Queue:", len(mpu0_queue))
        print("MPU1 Queue:", len(mpu1_queue))
        print("MPU2 Queue:", len(mpu2_queue))
        time.sleep(2)  # 每 2 秒打印一次队列内容

# 监听组合键的函数
def listen_for_exit():
    global running
    keyboard.add_hotkey('q', lambda: set_running_false())

def set_running_false():
    global running
    running = False

if __name__ == "__main__":
    # 启动一个线程读取串口数据
    thread = threading.Thread(target=read_data)
    thread.start()

    # 启动一个线程打印队列内容
    print_thread = threading.Thread(target=print_queues)
    print_thread.start()

    # 主线程监听组合键
    listen_for_exit()

    # 主线程保持运行状态，直到 running 变为 False
    while running:
        time.sleep(0.1)  # 让主线程保持运行状态

    # 等待其他线程结束
    thread.join()
    print_thread.join()
    ser.close()

    print("Program terminated.")