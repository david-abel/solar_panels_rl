#include <math.h>

int yAccelPin = A4;
int xAccelPin = A5;
int upPin = 7;
int downPin = 8;

int DOUBLE_PRECISION = 6;
double minX = 408;
double minY = 408;
double maxX = 618;
double maxY = 616;
double rangeX = 105;
double rangeY = 109;
double midpointX = 512;
double midpointY = 512;
double TOLERANCE = 0.017;


static double maxAngle = 1.1;
static double minAngle = -1.1;

bool isMovingDuration = false;

float getIncline() {
  double yAccel = analogRead(yAccelPin);
  double xAccel = analogRead(xAccelPin);
  double compensatedX = (xAccel - midpointX) / rangeX;
  double compensatedY = (yAccel - midpointY) / rangeY;
  double angle = atan2(compensatedY, -compensatedX);
  return angle;
}

void setup() {
  Serial.begin(9600);
  pinMode(yAccelPin, INPUT);
  pinMode(xAccelPin, INPUT);
  pinMode(upPin, OUTPUT);
  pinMode(downPin, OUTPUT);
  digitalWrite(upPin, HIGH);
  digitalWrite(downPin, HIGH);
  analogReference(EXTERNAL);
  
}

long goDurationStart = 0;
long goDurationEnd = 0;
void setupMoveForDuration(long duration) {
  Serial.println("Setting up move for duration");
  goDurationStart = millis();
  goDurationEnd = goDurationStart + duration;
  isMovingDuration = true;
}

double goDistanceStart = 0.0;
double goDistanceEnd = 0.0;
void setupMoveForDistance(double distance) {
  Serial.println("Setting up move for distance");
  goDistanceStart = getIncline();
  goDistanceEnd = goDistanceStart + distance;
}

bool goToPositionCoarse(double angle) {
  Serial.print("Going to "); Serial.println(angle, DOUBLE_PRECISION);
  double currentAngle = getIncline();
  if (fabs(currentAngle - angle) < TOLERANCE) {
    Serial.println("Not moving");
    digitalWrite(downPin, HIGH);
    digitalWrite(upPin, HIGH);
    return true;
  }
  else if (currentAngle > angle) {
    Serial.println("Going down");
    digitalWrite(downPin, LOW);
    digitalWrite(upPin, HIGH);
    return false;
  }
  else {
    Serial.println("Going up");
    digitalWrite(downPin, HIGH);
    digitalWrite(upPin, LOW);
    return false;
  }
  return false;
}

double APPROX_ANGULAR_VELOCITY = 0.05;
long startFineWait = 0;
long DELAY_FOR_MEASUREMENT = 1000;
bool moveUpward = false;
bool isMovingPosition = false;
bool goToPositionFine(double angle) {
  if (isMovingDuration) {
    if (goForDuration(moveUpward)) {
      Serial.println("Durational move complete, waiting to take measurement");
      isMovingDuration = false;
      startFineWait = millis();
    }
  } else if (millis() - startFineWait > DELAY_FOR_MEASUREMENT) {
    if (fabs(getIncline() - angle) < TOLERANCE) {
      Serial.println("Within tolerance of position, stopping move");
      return true;
    } else {
      Serial.println("Adjustment to position needed");
      double diff = getIncline() - angle;
      double estTimeToComplete = 1000.0 * fabs(diff) / APPROX_ANGULAR_VELOCITY;
      Serial.print("Angular difference "); Serial.println(diff, DOUBLE_PRECISION);
      Serial.print("Estimated move time "); Serial.println(estTimeToComplete, DOUBLE_PRECISION);
      setupMoveForDuration(estTimeToComplete);
      moveUpward = (getIncline() < angle);
      goForDuration(moveUpward);
    }
  }
  return false;
}

bool isMovingCoarsely = false;
bool isMovingFinely = false;
bool goToPosition(double angle) {
  Serial.print("Current angle "); Serial.println(getIncline(), DOUBLE_PRECISION);
  if (angle < minAngle){
    angle = minAngle;
  } else if (angle > maxAngle){
    angle = maxAngle;
  }
  
  
  if (!isMovingCoarsely && !isMovingFinely) {
    if (fabs(getIncline() - angle) < TOLERANCE) {
      Serial.println("Move already at position");
      return true;
    } else {
      Serial.println("Beginning move");
      isMovingCoarsely = true;
      goToPositionCoarse(angle);
    }
  } else if (isMovingCoarsely) {
    Serial.println("Moving to approximate location");
    if (goToPositionCoarse(angle)) {
      Serial.println("Coarse moving complete, starting fine moving");
      isMovingCoarsely = false;
      isMovingFinely = true;
      goToPositionFine(angle);
    } 
  } else {
    //Serial.println("Fine positioning");
      if (goToPositionFine(angle)) {
        Serial.println("Fine positioning complete");
        isMovingFinely = false;
        return true;
      }
    }
  return false;
}

bool goForDuration(bool upward) {
  if (millis() > goDurationEnd) {
    Serial.println("Not moving");
    digitalWrite(downPin, HIGH);
    digitalWrite(upPin, HIGH);
    return true;
  }
  else if (upward) {
    //Serial.println("Going up");
    digitalWrite(downPin, HIGH);
    digitalWrite(upPin, LOW);
    return false;
  }
  else {
    //Serial.println("Going down");
    digitalWrite(downPin, LOW);
    digitalWrite(upPin, HIGH);
    return false;
  }
  return false;
}

bool isStepSetup = false;
bool takeStep(double stepSize) {
  if (!isStepSetup) {
    setupMoveForDistance(stepSize);
    isStepSetup = true;
    return false;
  } else if(goToPosition(goDistanceEnd)) {
    isStepSetup = false;
    return true;
  }
  return false;
}

float stringToFloat(String str){
   char buffer[10];
   str.toCharArray(buffer, 10);
   return atof(buffer);
}

String msg;
static double stepSize = 0.1;


bool movingForward = false;
bool movingBackward = false;
bool movingToPosition = false;

float targetPos; 

void loop() {
  if (Serial.available()){
    msg = Serial.readString();
    
    if (msg.equals("F") && !movingForward && !movingBackward && !movingToPosition){
      //begin move
      movingForward = true;
    } else if (msg.equals("B") && !movingForward && !movingBackward && !movingToPosition){
      movingBackward = true;
    } else if (msg.charAt(0) == 'P' && !movingForward && !movingBackward && !movingToPosition){
      movingToPosition = true;
      targetPos = stringToFloat(msg.substring(1));
      Serial.println(targetPos);
    }
    
  }
  
  if (movingForward && takeStep(stepSize)){
    Serial.println("forward move completed!");
    movingForward = false;
  } else if (movingBackward && takeStep(-stepSize)){
    Serial.println("backward move completed!");
    movingBackward = false;
  } else if (movingToPosition && goToPosition(targetPos)){
    Serial.println("moved to target position!");
    movingToPosition = false;
  }

}
