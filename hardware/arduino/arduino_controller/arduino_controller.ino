//recieves commands from computer to move panel + sends data when requested

static int FORWARD_PIN = 7;
static int BACKWARD_PIN = 8;

//constants for voltage divider measurement.
const float R1 = 1000000.0;
const float R2 = 100000.0;
const float VREF = 5.0; //V, technically only valid if using external power source, USB power is ~4.83

float readVoltage; //V
float measuredVoltage; //V
float current; //A
float power; //W

//analog pins for current reading
const int A_PANEL = A3;
const int V_PANEL = A2;

const int A_ACTUATOR = A1;
const int V_ACTUATOR = A0;

/*
 * Converts analog pin reading to voltage. 
 */
float readingToVoltage(float reading){
  return (reading*VREF)/1023;
}

/*
 * Computes voltage reading from voltage divider. 
 */
float voltageDivider(float input){
  return (input)*(R1 + R2)/R2;
}

/*
 * Gets the wattage of the solar panel.
 */
float getPanelPower(){
  current = readingToVoltage(analogRead(A_PANEL));
  measuredVoltage = voltageDivider(readingToVoltage(analogRead(V_PANEL)));
  return current*measuredVoltage;
}

/*
 * Gets the wattage of the actuator.
 */
float getActuatorPower(){
  current = readingToVoltage(analogRead(A_ACTUATOR));
  measuredVoltage = voltageDivider(readingToVoltage(analogRead(V_ACTUATOR)));
  return current*measuredVoltage;
}

static int MAX_READINGS = 100;

int powerReadings[MAX_READINGS];

/*
 * collects power readings for the specified duration. 
 */
float measurePowerForDuration(String device, int duration, int timeStep){
  
}


void setup() {
  // set pinMode to high, to prevent motion
  pinMode(FORWARD_PIN, OUTPUT);
  pinMode(BACKWARD_PIN, OUTPUT);

  digitalWrite(FORWARD_PIN, HIGH);
  digitalWrite(BACKWARD_PIN, HIGH);

  //initializing serial
  Serial.begin(9600);

}

String msg;

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()){
    msg = Serial.readString();
    if (msg.equals("FORWARD")){
      Serial.println("moving forward");
      digitalWrite(FORWARD_PIN, LOW);
      delay(1000);
      digitalWrite(FORWARD_PIN, HIGH);
      Serial.println("moved forward, took XXX energy");
    } else if (msg.equals("BACKWARD")){
      Serial.println("moving backward");
      digitalWrite(BACKWARD_PIN, LOW);
      delay(1000);
      digitalWrite(BACKWARD_PIN, HIGH);
      Serial.println("moved backward, took XXX energy");
    } else if (msg.equals("DATA")){
      Serial.print("Current solar panel power output ");
      Serial.print(getPanelPower());
    } else {
      Serial.println("UNRECOGNIZED COMMAND");
    }
  }
  
}
