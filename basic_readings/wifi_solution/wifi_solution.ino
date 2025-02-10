#include <ArduinoBLE.h> // 使用 Arduino BLE 库
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Arduino.h>
#include "TCA9548A.h"

TCA9548A I2CMux;  
Adafruit_MPU6050 mpu0, mpu1, mpu2;

// **定义 BLE 服务和特征**
BLEService mpuService("180C");  // 自定义 BLE 服务 UUID
BLECharacteristic mpuDataCharacteristic("2A56", BLERead | BLENotify, 50); // 50 字节的特征

void configureMPU(Adafruit_MPU6050 &mpu) {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_1000_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

void setup() {
    Serial.begin(115200);
    Wire.begin();

    I2CMux.begin(Wire);
    I2CMux.closeAll();

    I2CMux.openChannel(2);
    if (!mpu0.begin()) Serial.println("无法找到 MPU6050 设备 2");
    else configureMPU(mpu0);
    I2CMux.closeAll();

    I2CMux.openChannel(4);
    if (!mpu1.begin()) Serial.println("无法找到 MPU6050 设备 4");
    else configureMPU(mpu1);
    I2CMux.closeAll();

    I2CMux.openChannel(6);
    if (!mpu2.begin()) Serial.println("无法找到 MPU6050 设备 6");
    else configureMPU(mpu2);
    I2CMux.closeAll();

    // **初始化 BLE**
    if (!BLE.begin()) {
        Serial.println("启动 BLE 失败！");
        while (1);
    }

    // **设置 BLE 设备名称**
    BLE.setLocalName("GestureDevice");
    BLE.setAdvertisedService(mpuService);
    mpuService.addCharacteristic(mpuDataCharacteristic);
    BLE.addService(mpuService);

    // **开始广播 BLE**
    BLE.advertise();
    Serial.println("wait BLE connect...");
}

void loop() {
    BLEDevice central = BLE.central();  // 检测 BLE 连接

    if (central) {
        Serial.print("连接到: ");
        Serial.println(central.address());

        while (central.connected()) {
            sensors_event_t a, g, temp;
            String data = "";

            I2CMux.openChannel(2);
            mpu0.getEvent(&a, &g, &temp);
            data = "MPU0," + String(a.acceleration.x) + "," + String(a.acceleration.y) + "," + String(a.acceleration.z) + "," +
                    String(g.gyro.x) + "," + String(g.gyro.y) + "," + String(g.gyro.z) + "\n";
            I2CMux.closeAll();
                        // **通过 BLE 发送数据**
            mpuDataCharacteristic.writeValue(data.c_str());
            Serial.println(data);

            I2CMux.openChannel(4);
            mpu1.getEvent(&a, &g, &temp);
            data = "MPU1," + String(a.acceleration.x) + "," + String(a.acceleration.y) + "," + String(a.acceleration.z) + "," +
                    String(g.gyro.x) + "," + String(g.gyro.y) + "," + String(g.gyro.z) + "\n";
            I2CMux.closeAll();
                        // **通过 BLE 发送数据**
            mpuDataCharacteristic.writeValue(data.c_str());
            Serial.println(data);

            I2CMux.openChannel(6);
            mpu2.getEvent(&a, &g, &temp);
            data = "MPU2," + String(a.acceleration.x) + "," + String(a.acceleration.y) + "," + String(a.acceleration.z) + "," +
                    String(g.gyro.x) + "," + String(g.gyro.y) + "," + String(g.gyro.z) + "\n";
            I2CMux.closeAll();
                        // **通过 BLE 发送数据**
            mpuDataCharacteristic.writeValue(data.c_str());
            Serial.println(data);


            delay(50);
        }

        Serial.println("BLE disconnect");
    }
}


