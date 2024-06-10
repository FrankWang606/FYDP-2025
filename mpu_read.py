import serial
from collections import deque
import threading
import time
from mpudata import MPUData 


# 设置串口参数
ser = serial.Serial('COM3', 9600)  # 根据实际情况更改COM端口

# 创建三个双端队列，每个队列最多存储20组数据
mpu0_queue = deque(maxlen=50)
mpu1_queue = deque(maxlen=50)
mpu2_queue = deque(maxlen=50)

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
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            mpu_name, mpu_data = parse_data(data)
            if mpu_name == "MPU0":
                mpu0_queue.append(mpu_data)
            elif mpu_name == "MPU1":
                mpu1_queue.append(mpu_data)
            elif mpu_name == "MPU2":
                mpu2_queue.append(mpu_data)

# 启动一个线程读取串口数据
thread = threading.Thread(target=read_data)
thread.start()

# 打印队列内容的函数，用于测试
def print_queues():
    while True:
        print("MPU0 Queue:", len(mpu0_queue))
        print("MPU1 Queue:", len(mpu1_queue))
        print("MPU2 Queue:", len(mpu2_queue))
        time.sleep(2)  # 每2秒打印一次队列内容

# 启动一个线程打印队列内容
print_thread = threading.Thread(target=print_queues)
print_thread.start()