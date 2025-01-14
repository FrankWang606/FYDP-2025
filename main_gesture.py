import sys
import json
import serial
from collections import deque
import threading
import time
import keyboard  # 导入 keyboard 库
from mpudata import MPUData
import rec_algorithm as Recognizer 

def mpu_data_to_dict(obj):
    """将 MPUData 对象转换为字典"""
    if isinstance(obj, MPUData):
        return {
            "ax": obj.ax,
            "ay": obj.ay,
            "az": obj.az,
            "rx": obj.rx,
            "ry": obj.ry,
            "rz": obj.rz,
        }
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


lock = threading.Lock()
# pause_event = threading.Event()

current_gesture = -1 # 0 thumb up, 1 thumb down, 2 wave, 3 pinch in, 4 palm flip, 5 self record
# 设置串口参数
ser = serial.Serial('COM3', 9600)  # 根据实际情况更改 COM 端口

# 创建三个双端队列
mpu0_queue = deque(maxlen=15)
mpu1_queue = deque(maxlen=15)
mpu2_queue = deque(maxlen=15)

# 定义新的全局变量用于存储录制的手势数据
recorded_mpu0_queue = deque(maxlen=15)
recorded_mpu1_queue = deque(maxlen=15)
recorded_mpu2_queue = deque(maxlen=15)

thumbup_0 = deque(maxlen=5)
thumbup_1 = deque(maxlen=5)
thumbup_2 = deque(maxlen=5)
thumbdown_0 = deque(maxlen=5)
thumbdown_1 = deque(maxlen=5)
thumbdown_2 = deque(maxlen=5)
pinch_0 = deque(maxlen=15)
pinch_1 = deque(maxlen=15)
pinch_2 = deque(maxlen=15)
# 定义一个标志位用于控制线程的运行
running = True

def load_recorded_data(file_path):
    """从 JSON 文件加载录制手势数据并还原为 MPUData 队列"""
    with open(file_path, "r") as f:
        data = json.load(f)
    
    recorded_data = {
        "mpu0": deque([MPUData(**mpu) for mpu in data["mpu0"]], maxlen=15),
        "mpu1": deque([MPUData(**mpu) for mpu in data["mpu1"]], maxlen=15),
        "mpu2": deque([MPUData(**mpu) for mpu in data["mpu2"]], maxlen=15),
    }
    return recorded_data

def read_ges_record():
    """读取 ges_record.txt 中的值"""
    try:
        with open("ges_record.txt", "r") as file:
            value = file.read().strip()
            return int(value)  # 将值转换为整数
    except Exception as e:
        print(f"Error reading ges_record.txt: {e}")
        return -1  # 如果读取失败，返回默认值
    
def record_gesture():
    global running,recorded_mpu0_queue, recorded_mpu1_queue, recorded_mpu2_queue
    while running:
        if read_ges_record() == 1:  # 进入录制模式
            recorded_data = {"mpu0": [], "mpu1": [], "mpu2": []}
            print("Recording gesture...")

            while len(recorded_data["mpu0"]) < 15:
                # 检查队列中的最新数据
                if len(mpu0_queue) > 0 and len(recorded_data["mpu0"]) < 15:
                    mpu0_last = mpu0_queue[-1]
                    if len(recorded_data["mpu0"]) == 0 or mpu0_last != recorded_data["mpu0"][-1]:
                        recorded_data["mpu0"].append(mpu0_last)

                if len(mpu1_queue) > 0 and len(recorded_data["mpu1"]) < 15:
                    mpu1_last = mpu1_queue[-1]
                    if len(recorded_data["mpu1"]) == 0 or mpu1_last != recorded_data["mpu1"][-1]:
                        recorded_data["mpu1"].append(mpu1_last)

                if len(mpu2_queue) > 0 and len(recorded_data["mpu2"]) < 15:
                    mpu2_last = mpu2_queue[-1]
                    if len(recorded_data["mpu2"]) == 0 or mpu2_last != recorded_data["mpu2"][-1]:
                        recorded_data["mpu2"].append(mpu2_last)

                time.sleep(0.01)  # 稍作延迟避免过度占用资源

            # 保存录制数据到文件
            with open("recorded_patterns.json", "w") as f:
                json.dump(recorded_data, f, default=mpu_data_to_dict)
                f.write("\n")
            
            # 将录制的数据直接加载到新的队列中
            recorded_mpu0_queue = deque(recorded_data["mpu0"], maxlen=15)
            recorded_mpu1_queue = deque(recorded_data["mpu1"], maxlen=15)
            recorded_mpu2_queue = deque(recorded_data["mpu2"], maxlen=15)

            print("Gesture recorded successfully!")
            record_state_print(-1)  # 重置状态
            
        time.sleep(0.1)


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
        mpu0 = deque(list(mpu0_queue)[-5:], maxlen=5)
        mpu1 = deque(list(mpu1_queue)[-5:], maxlen=5)
        mpu2 = deque(list(mpu2_queue)[-5:], maxlen=5)

        if(Recognizer.record(mpu0,mpu1,mpu2,thumbup_0,thumbup_1,thumbup_2,3.5)):
            with lock:
                current_gesture = 0
            time.sleep(3)
            
def ges_thumb_down():
    global current_gesture,running
    while running:
        time.sleep(0.05)
        mpu0 = deque(list(mpu0_queue)[-5:], maxlen=5)
        mpu1 = deque(list(mpu1_queue)[-5:], maxlen=5)
        mpu2 = deque(list(mpu2_queue)[-5:], maxlen=5)

        if(Recognizer.record(mpu0,mpu1,mpu2,thumbdown_0,thumbdown_1,thumbdown_2,3.5)):
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
        time.sleep(0.05)
        mpu0 = mpu0_queue
        mpu1 = mpu1_queue
        mpu2 = mpu2_queue

        if(Recognizer.record(mpu0,mpu1,mpu2,pinch_0,pinch_1,pinch_2,4.5)):
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

def ges_record():
    global current_gesture,running
    while running:
        time.sleep(0.05)
        mpu0 = mpu0_queue
        mpu1 = mpu1_queue
        mpu2 = mpu2_queue
        if(Recognizer.record(mpu0,mpu1,mpu2,recorded_mpu0_queue,recorded_mpu1_queue,recorded_mpu2_queue)):
            with lock:
                current_gesture = 5
            time.sleep(3)

def set_running_false():
    global running
    running = False
    
def current_state_print(state):
    with open('gesture.txt', 'w') as f:
        f.write(str(state))
        
def record_state_print(state):
    with open('ges_record.txt', 'w') as f:
        f.write(str(state))

if __name__ == "__main__":
    keyboard.add_hotkey('q', lambda: set_running_false())
    record_state_print(-1)
    # 启动一个线程读取串口数据
    thread = threading.Thread(target=read_data)
    thread.start()
    
    ges_data = load_recorded_data('thumbup.json')
    thumbup_0 = deque(list(ges_data["mpu0"])[-5:], maxlen=5)
    thumbup_1 = deque(list(ges_data["mpu1"])[-5:], maxlen=5)
    thumbup_2 = deque(list(ges_data["mpu2"])[-5:], maxlen=5)
    ges_data = load_recorded_data('thumbdown.json')
    thumbdown_0 = deque(list(ges_data["mpu0"])[-5:], maxlen=5)
    thumbdown_1 = deque(list(ges_data["mpu1"])[-5:], maxlen=5)
    thumbdown_2 = deque(list(ges_data["mpu2"])[-5:], maxlen=5)
    ges_data = load_recorded_data('pinchin.json')
    pinch_0 = deque(ges_data["mpu0"], maxlen=15)
    pinch_1 = deque(ges_data["mpu1"], maxlen=15)
    pinch_2 = deque(ges_data["mpu2"], maxlen=15)

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
    ges6 = threading.Thread(target=ges_record)
    ges6.start()

    # 启动录制线程
    record_thread = threading.Thread(target=record_gesture)
    record_thread.start()

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
    record_thread.join()
    ser.close()

    print("Program terminated.")
    sys.exit(0)