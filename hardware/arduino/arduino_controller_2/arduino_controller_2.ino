//recieves actions from computer over serial + returns reward

static int FORWARD_PIN = 7;
static int BACKWARD_PIN = 8;

//constants for voltage divider measurement.
//These are measured from the panel voltmeter circuit 
const float R1_panel = 1010000.0;
const float R2_panel = 99700.0;
const float R1_actuator = 1023000.0;
const float R2_actuator = 99500.0;
const float VREF = 4.88; //V, technically only valid if using external power source, USB power is ~4.88

float readVoltage; //V
float measuredVoltage; //V
float amps; //A
float power; //W

//analog pins for current reading
const int A_PANEL = A3;
const int V_PANEL = A2;

const int A_ACTUATOR = A1;
const int V_ACTUATOR = A0;


float netEnergyDuringTimestep; //count of net energy collected during this cycle, will be reset on query

float lastPower; //last power reading (difference of panel input - actuator consumption)
float currentPower; //current power reading

//markers to check if moving is happening
bool movingForwards; 
bool movingBackwards; 
bool nullAction; 

//tracking time in milliseconds
unsigned long lastTime;
unsigned long currentTime;

unsigned long actionStartTime; //tracking action duration

static unsigned long actionDuration = 3000; //ms for action duration

String action;

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
 * recieving action from serial communication
 * sends current energy count (reward), resets it to zero
 * Checking to avoid action conflicts
 */
void handleIncomingAction(){
  //check if serial is available 
  if (Serial.available()){
    action = Serial.readString();
    if (action.equals("FW")){
      if (!movingForwards && !movingBackwards && !nullAction){
        actionStartTime = currentTime;
        movingForwards = true;
        digitalWrite(FORWARD_PIN, LOW);
      }
    } else if (action.equals("BW")){
      if (!movingForwards && !movingBackwards && !nullAction){
        actionStartTime = currentTime;
        movingBackwards = true;
        digitalWrite(BACKWARD_PIN, LOW);
      }
      
    } else if (action.equals("NA")){
      //sets the nullAction flag to true 
      //establishing a separation between this method and the completion one, only that method handles transmission
      if (!movingForwards && !movingBackwards && !nullAction){
        nullAction = true;
      }
    } // else {
//      //cmd not recognized
//      //do nothing I guess
//    }
  
  }

}

/*
 * Checks if the action has been completed, sends final energy results
 * For now, using simple duration-based moving actions
 */
void checkActionCompletion(){
  if (nullAction){
    Serial.println("NULL ACTION COMPLETED"); //TODO: remove this debug phrase
    Serial.println(netEnergyDuringTimestep);
    netEnergyDuringTimestep = 0;
    nullAction = false;
  } else if (movingForwards && currentTime - actionStartTime >= actionDuration){
    Serial.println("FORWARD ACTION COMPLETED"); //debug phrase
    Serial.println(netEnergyDuringTimestep);
    netEnergyDuringTimestep = 0;
    movingForwards = false;
    digitalWrite(FORWARD_PIN, HIGH); //back to off
  } else if (movingBackwards && currentTime - actionStartTime >= actionDuration){
    Serial.println("BACKWARD ACTION COMPLETED"); //debug
    Serial.println(netEnergyDuringTimestep);
    netEnergyDuringTimestep = 0;
    movingBackwards = false;
    digitalWrite(BACKWARD_PIN, HIGH);
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

void setup() {
  // set pinMode to high, to prevent motion
  pinMode(FORWARD_PIN, OUTPUT);
  pinMode(BACKWARD_PIN, OUTPUT);

  digitalWrite(FORWARD_PIN, HIGH);
  digitalWrite(BACKWARD_PIN, HIGH);

  //initializing serial
  Serial.begin(9600);

  //initialize panel panel power + net energy
  netEnergyDuringTimestep = 0;
  lastPower = 0;
  currentPower = 0;
  
  movingForwards = false;
  movingBackwards = false;
  nullAction = false;

  currentTime = 0;
  lastTime = 0;
  actionStartTime = 0; 
}


/*
 * Main loop:
 * updates energy reading
 * handles incoming actions from computer, starts motion if required
 * checks for action completion, stops action and sends current reading if so
 */
void loop() {
  //update current time
  currentTime = millis();
  //perform main loop
  updateEnergy();
  handleIncomingAction();
  checkActionCompletion();
  lastTime = currentTime;
}
