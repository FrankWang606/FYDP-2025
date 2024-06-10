#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <Arduino.h>
#include "TCA9548A.h"

TCA9548A I2CMux;  
Adafruit_MPU6050 mpu0;
Adafruit_MPU6050 mpu1;
Adafruit_MPU6050 mpu2;

void configureMPU(Adafruit_MPU6050 &mpu) {
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_1000_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

void setup(void) {
  Serial.begin(9600);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  Wire.begin();
  I2CMux.begin(Wire);             // Wire instance is passed to the library
  I2CMux.closeAll();              // Set a base state which we know (also the default state on power on)

  I2CMux.openChannel(2);
  if (!mpu0.begin()) {
    Serial.println("Failed to find MPU6050 chip 2");
    while (1) {
      delay(10);
    }
  }
  configureMPU(mpu0);
  I2CMux.closeAll();

  I2CMux.openChannel(4);
  if (!mpu1.begin()) {
    Serial.println("Failed to find MPU6050 chip 4");
    while (1) {
      delay(10);
    }
  }
  configureMPU(mpu1);
  I2CMux.closeAll();

  I2CMux.openChannel(6);
  if (!mpu2.begin()) {
    Serial.println("Failed to find MPU6050 chip 6");
    while (1) {
      delay(10);
    }
  }
  configureMPU(mpu2);
  I2CMux.closeAll();
}

void loop() {
  sensors_event_t a, g, temp;

  I2CMux.openChannel(2);
  mpu0.getEvent(&a, &g, &temp);
  Serial.print("MPU0,");
  Serial.print(a.acceleration.x); Serial.print(",");
  Serial.print(a.acceleration.y); Serial.print(",");
  Serial.print(a.acceleration.z); Serial.print(",");
  Serial.print(g.gyro.x); Serial.print(",");
  Serial.print(g.gyro.y); Serial.print(",");
  Serial.print(g.gyro.z); Serial.println();
  I2CMux.closeAll();

  I2CMux.openChannel(4);
  mpu1.getEvent(&a, &g, &temp);
  Serial.print("MPU1,");
  Serial.print(a.acceleration.x); Serial.print(",");
  Serial.print(a.acceleration.y); Serial.print(",");
  Serial.print(a.acceleration.z); Serial.print(",");
  Serial.print(g.gyro.x); Serial.print(",");
  Serial.print(g.gyro.y); Serial.print(",");
  Serial.print(g.gyro.z); Serial.println();
  I2CMux.closeAll();


  I2CMux.openChannel(6);
  mpu2.getEvent(&a, &g, &temp);
  Serial.print("MPU2,");
  Serial.print(a.acceleration.x); Serial.print(",");
  Serial.print(a.acceleration.y); Serial.print(",");
  Serial.print(a.acceleration.z); Serial.print(",");
  Serial.print(g.gyro.x); Serial.print(",");
  Serial.print(g.gyro.y); Serial.print(",");
  Serial.print(g.gyro.z); Serial.println();
  I2CMux.closeAll();

}