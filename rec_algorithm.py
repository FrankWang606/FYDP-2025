
from collections import deque
import time
import keyboard  # 导入 keyboard 库
from mpudata import MPUData

def thumb_up(mpu0,mpu1):
    if len(mpu0) <= 5 or len(mpu1) <= 5:
        return False
    # pause_event.wait()
    avg_ax0 = (mpu0[-1].ax + mpu0[-2].ax + mpu0[-3].ax + mpu0[-4].ax)/4
    avg_ay1 = (mpu1[-1].ay + mpu1[-2].ay + mpu1[-3].ay + mpu1[-4].ay)/4
    avg_az1 = (mpu1[-1].az + mpu1[-2].az + mpu1[-3].az + mpu1[-4].az)/4
    if avg_ax0 >=7 and avg_ay1<=-8 and avg_az1<=-3:
        return True
    return False