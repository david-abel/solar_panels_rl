#include <math.h>

//integrating accurate motion code with data collection code

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


static int FORWARD_PIN = 7;
static int BACKWARD_PIN = 8;

//constants for voltage divider measurement.
//These are measured from the panel voltmeter circuits  
const float R1_panel = 1010000.0;
const float R2_panel = 99700.0;
const float R1_actuator = 1023000.0;
const float R2_actuator = 99500.0;
const float VREF = 3.0; //using reference voltage from regulator 

float readVoltage; //V
float measuredVoltage; //V
float amps; //A
float power; //W

//analog pins for current reading
const int A_PANEL = A3;
const int V_PANEL = A2;

const int A_ACTUATOR = A1;
const int V_ACTUATOR = A0;

float netEnergyDuringTimestep = 0; //count of net energy collected during this cycle, will be reset on action completion

float lastPower = 0; //last power reading (difference of panel input - actuator consumption)
float currentPower = 0; //current power reading

//tracking time in milliseconds
unsigned long lastTime = 0;
unsigned long currentTime = 0;

/*
 * Converts analog pin reading to voltage. 
 */
float readingToVoltage(float reading){
  return (reading*VREF)/1023;
}

/*
 * Computes voltage reading from voltage divider. 
 */
float voltageDivider(float input, boolean actuator){
  if (actuator){
    return (input)*(R1_actuator + R2_actuator)/R2_actuator;
  } else {
    return (input)*(R1_panel + R2_panel)/R2_panel;
  }

}

/*
 * Updates net energy count using readings from panel and actuator 
 */
void updateEnergy(){
  //get current power reading
  //actuator power will be zero unless something is happening
  currentPower = getPanelPower() - getActuatorPower();
  //compute energy consumed during this timestep 
  //integral of power during this timestep approximated with trapezoids
  netEnergyDuringTimestep += 0.5*(currentPower + lastPower)*((currentTime - lastTime)/1000.0);
  
  lastPower = currentPower;
}

/*
 * Gets the wattage of the actuator.
 */
float getActuatorPower(){
  amps = readingToVoltage(analogRead(A_ACTUATOR));
  measuredVoltage = voltageDivider(readingToVoltage(analogRead(V_ACTUATOR)), true);
  return amps*measuredVoltage;
}

/*
 * Gets the wattage of the solar panel.
 */
float getPanelPower(){
  amps = readingToVoltage(analogRead(A_PANEL));
  measuredVoltage = voltageDivider(readingToVoltage(analogRead(V_PANEL)), false);
  return amps*measuredVoltage;
}


/*
*computes incline from accellerometer. 
*/
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
//TODO: 
static double defaultStep = 0.1;

bool movingForward = false;
bool movingBackward = false;
bool takingStep = false;
bool nullAction = false;
bool movingToPosition = false;

//for convenience
bool noActionOccuring;

float targetPos; 
float currentStepSize;

void handleIncomingAction(){
  //check if serial is available
   if (Serial.available()){
    msg = Serial.readString();

    noActionOccuring = !takingStep && !movingToPosition && !nullAction;
    
    //F or B: take a step with the default step size
    //N: no action
    //S followed by number: take a step with provided step size
    //P followed by number: go to provided position

    if (msg.equals("F") && noActionOccuring){
      takingStep = true;
      currentStepSize = defaultStep;
    } else if (msg.equals("B") && noActionOccuring){
      takingStep = true;
      currentStepSize = -defaultStep;
    } else if (msg.equals("N") && noActionOccuring){
      nullAction = true;
    } else if (msg.charAt(0) == 'S' && noActionOccuring){
      takingStep = true;
      currentStepSize = stringToFloat(msg.substring(1));
    } else if (msg.charAt(0) == 'P' && noActionOccuring){
      movingToPosition = true;
      targetPos = stringToFloat(msg.substring(1));
    }
    
  }
}
/*
*This loop is actually what triggers the actions, not just checking for completion.
*calling each of takeStep, goToPosition for the first time triggers the action. 
*/
void checkActionCompletion(){
  if (takingStep && takeStep(currentStepSize)){
    Serial.println("step completed!");
    Serial.println(netEnergyDuringTimestep);
    netEnergyDuringTimestep = 0;
    takingStep = false;
  } else if (movingToPosition && goToPosition(targetPos)){
    Serial.println("moved to target position!");
    Serial.println(netEnergyDuringTimestep);
    netEnergyDuringTimestep = 0;
    movingToPosition = false;
  } else if (nullAction){
    Serial.println("null action! nothing happened!");
    Serial.println(netEnergyDuringTimestep);
    netEnergyDuringTimestep = 0;
    nullAction = false; 
  }
}

void loop() {
  currentTime = millis();
  updateEnergy();
  handleIncomingAction();
  checkActionCompletion();
  lastTime = currentTime;

}
