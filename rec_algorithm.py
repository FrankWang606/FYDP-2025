
from collections import deque
import time
from mpudata import MPUData
import math

def calculate_distance(mpu_data1, mpu_data2):
    """计算两个 MPUData 对象的欧几里得距离"""
    return math.sqrt(
        (mpu_data1.ax - mpu_data2.ax) ** 2 +
        (mpu_data1.ay - mpu_data2.ay) ** 2 +
        (mpu_data1.az - mpu_data2.az) ** 2 +
        (mpu_data1.rx - mpu_data2.rx) ** 2 +
        (mpu_data1.ry - mpu_data2.ry) ** 2 +
        (mpu_data1.rz - mpu_data2.rz) ** 2
    )

def thumb_up(mpu0,mpu1):
    if len(mpu0) <= 5 or len(mpu1) <= 5:
        return False
    # pause_event.wait()
    avg_ax0 = (mpu0[-1].ax + mpu0[-2].ax + mpu0[-3].ax + mpu0[-4].ax)/4
    avg_ay1 = (mpu1[-1].ay + mpu1[-2].ay + mpu1[-3].ay + mpu1[-4].ay)/4
    avg_az1 = (mpu1[-1].az + mpu1[-2].az + mpu1[-3].az + mpu1[-4].az)/4
    if avg_ax0 >=8 and avg_ay1<=-8 and avg_az1<=0:
        return True
    return False

def thumb_down(mpu0,mpu1):
    if len(mpu0) <= 5 or len(mpu1) <= 5:
        return False
    # pause_event.wait()
    avg_ax0 = (mpu0[-1].ax + mpu0[-2].ax + mpu0[-3].ax + mpu0[-4].ax)/4
    avg_ay1 = (mpu1[-1].ay + mpu1[-2].ay + mpu1[-3].ay + mpu1[-4].ay)/4
    avg_az1 = (mpu1[-1].az + mpu1[-2].az + mpu1[-3].az + mpu1[-4].az)/4
    if avg_ax0 <=-7 and avg_ay1>=8 and avg_az1>=-1:
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

    mpu1_condition = (diff_az1>20 and (max_az1 > 30 or min_az1 <-35) and az1_stable_count >=9)
    if mpu1_condition :
        return True
    return False

def flip(mpu0,mpu1,mpu2):
    if len(mpu0) < 15 or len(mpu1) < 15 or len(mpu2)<15:
        return False
    # pause_event.wait()
    cond_az0_pos1 = (mpu0[0].az > 8 or mpu0[1].az >8 or mpu0[2].az >8)
    cond_az0_pos2 = (mpu0[-1].az < -5 or mpu0[-2].az < -5 or mpu0[-3].az < -5)
    cond_az0_neg1 = (mpu0[0].az < -5 or mpu0[1].az < -5 or mpu0[2].az < -5)
    cond_az0_neg2 = (mpu0[-1].az > 8 or mpu0[-2].az >8 or mpu0[-3].az >8)
    mpu0_condition = (cond_az0_pos1 and cond_az0_pos2) or (cond_az0_neg1 and cond_az0_neg2)
    
    cond_az1_pos1 = (mpu1[0].az > 8 or mpu1[1].az >8 or mpu1[2].az >8)
    cond_az1_pos2 = (mpu1[-1].az < -8 or mpu1[-2].az < -8 or mpu1[-3].az < -8)
    cond_az1_neg1 = (mpu1[0].az < -8 or mpu1[1].az < -8 or mpu1[2].az < -8)
    cond_az1_neg2 = (mpu1[-1].az > 8 or mpu1[-2].az >8 or mpu1[-3].az >8)
    mpu1_condition = (cond_az1_pos1 and cond_az1_pos2) or (cond_az1_neg1 and cond_az1_neg2)
    
    cond_az2_pos1 = (mpu2[0].az > 8 or mpu2[1].az >8 or mpu2[2].az >8)
    cond_az2_pos2 = (mpu2[-1].az < -8 or mpu2[-2].az < -8 or mpu2[-3].az < -8)
    cond_az2_neg1 = (mpu2[0].az < -8 or mpu2[1].az < -8 or mpu2[2].az < -8)
    cond_az2_neg2 = (mpu2[-1].az > 8 or mpu2[-2].az >8 or mpu2[-3].az >8)
    mpu2_condition = (cond_az2_pos1 and cond_az2_pos2) or (cond_az2_neg1 and cond_az2_neg2)
    if mpu1_condition and mpu2_condition and mpu0_condition:
        return True
    return False

def record(mpu0, mpu1, mpu2, mpu_record0, mpu_record1, mpu_record2, threshold=4.5):
    """比较实时手势和录制手势数据，判断相似性"""
    if len(mpu0) != len(mpu_record0) or len(mpu1) != len(mpu_record1) or len(mpu2) != len(mpu_record2):
        return False

    def calculate_average_distance(real, recorded):
        distances = [calculate_distance(real[i], recorded[i]) for i in range(len(real))]
        return sum(distances) / len(distances)

    avg_distance_mpu0 = calculate_average_distance(mpu0, mpu_record0)
    avg_distance_mpu1 = calculate_average_distance(mpu1, mpu_record1)
    avg_distance_mpu2 = calculate_average_distance(mpu2, mpu_record2)

    if threshold == 4.0:
        print(f"MPU0 Avg Distance: {avg_distance_mpu0}, MPU1 Avg Distance: {avg_distance_mpu1}, MPU2 Avg Distance: {avg_distance_mpu2}")

    # 判断所有平均距离是否小于阈值
    return avg_distance_mpu0 < threshold and avg_distance_mpu1 < threshold and avg_distance_mpu2 < threshold