#include <math.h>

int yAccelPin = A4;
int xAccelPin = A5;
double minX = 266.0;
double minY = 266.0;
double maxX = 402.0;
double maxY = 402.0;
double rangeX = 68.0;
double rangeY = 68.0;
double midpointX = 334.0;
double midpointY = 334.0;

void calibrate(float xAccel, float yAccel) {
  if (xAccel < minX) {
    minX = xAccel;
  }
  if (xAccel > maxX) {
    maxX = xAccel;
  }
  if (yAccel < minY) {
    minY = yAccel;
  }
  if (yAccel > maxY) {
    maxY = yAccel;
  }
  rangeX = 0.5 * (maxX - minX);
  rangeY = 0.5 * (maxY - minY);
  midpointX = minX + rangeX;
  midpointY = minY + rangeY;
  Serial.print("X min "); Serial.print(minX);
  Serial.print("\tX max "); Serial.println(maxX);
  Serial.print("Y min "); Serial.print(minY);
  Serial.print("\tY max "); Serial.println(maxY);
}

float getIncline() {
  double yAccel = analogRead(yAccelPin);
  double xAccel = analogRead(xAccelPin);
  Serial.print("X accel ");
  Serial.print(xAccel);
  Serial.print("\t Y accel ");
  Serial.println(yAccel);
  //calibrate(xAccel, yAccel);
  
  double compensatedX = (xAccel - midpointX) / rangeX;
  double compensatedY = (yAccel - midpointY) / rangeY;
  Serial.print("X comp ");
  Serial.print(compensatedX);
  Serial.print("\t Y comp ");
  Serial.println(compensatedY);
  double angle = atan2(compensatedY, -compensatedX);
  Serial.print("Incline: ");
  Serial.println(angle);
  return angle;
}

void setup() {
  Serial.begin(9600);
  // put your setup code here, to run once:
  pinMode(yAccelPin, INPUT);
  pinMode(xAccelPin, INPUT);
}



void loop() {
  Serial.println(getIncline());
  delay(1000);
}
