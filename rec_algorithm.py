
from collections import deque
import time
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

def thumb_down(mpu0,mpu1):
    if len(mpu0) <= 5 or len(mpu1) <= 5:
        return False
    # pause_event.wait()
    avg_ax0 = (mpu0[-1].ax + mpu0[-2].ax + mpu0[-3].ax + mpu0[-4].ax)/4
    avg_ay1 = (mpu1[-1].ay + mpu1[-2].ay + mpu1[-3].ay + mpu1[-4].ay)/4
    avg_az1 = (mpu1[-1].az + mpu1[-2].az + mpu1[-3].az + mpu1[-4].az)/4
    if avg_ax0 <=-7.5 and avg_ay1>=8 and avg_az1>=0:
        return True
    return False

def wave(mpu0,mpu2):
    if len(mpu0) < 15 or len(mpu2) < 15:
        return False
    # pause_event.wait()
    max_ax0 = -10
    min_ax0 = 10
    max_rz0 = -10
    min_rz0 = 10
    max_ay2 = -10
    min_ay2 = 10
    max_rz2 = -10
    min_rz2 = 10
    for i in range(0,len(mpu0)):
        max_ax0 = max(max_ax0,mpu0[i].ax)
        min_ax0 = min(min_ax0,mpu0[i].ax)
        max_rz0 = max(max_rz0,mpu0[i].rz)
        min_rz0 = min(min_rz0,mpu0[i].rz)
        max_ay2 = max(max_ay2,mpu2[i].ay)
        min_ay2 = min(min_ay2,mpu2[i].ay)
        max_rz2 = max(max_rz2,mpu2[i].rz)
        min_rz2 = min(min_rz2,mpu2[i].rz)
    diff_ax0 = max_ax0 - min_ax0
    
    mpu0_condition =(max_ax0 >=9 and min_ax0<=7 and max_rz0>=2 and min_rz0<=-2 and diff_ax0>2.5)
    mpu1_condition =(max_ay2>12 and min_ay2<-13 and max_rz2>2 and min_rz2<-2)
    if mpu1_condition and mpu0_condition:
        return True
    return False

def pinch(mpu0,mpu1):
    if len(mpu0) < 15 or len(mpu1) < 15:
        return False
    # pause_event.wait()

    max_az1 = -10
    min_az1 = 10
    az1_stable_count = 0
    avg_stable_az1 = 0
    for i in range(1,len(mpu0)-1):
        if(abs(mpu1[i-1].az-mpu1[i].az)<0.9  and abs(mpu1[i+1].az-mpu1[i].az)<0.9):
            avg_stable_az1 += mpu1[i].az
            az1_stable_count += 1

    if az1_stable_count > 0:
        avg_stable_az1 = avg_stable_az1/az1_stable_count
    for i in range(0,len(mpu0)):
        max_az1 = max(max_az1,mpu1[i].az)
        min_az1 = min(min_az1,mpu1[i].az)

    diff_az1 = max_az1 - min_az1

    mpu1_condition = (diff_az1>25 and avg_stable_az1 > 2 and az1_stable_count >=9)
    if mpu1_condition :
        return True
    return False