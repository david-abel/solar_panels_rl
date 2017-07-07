//testing current by measuring across LED connected to arduino power supply
//const int LED_PIN = 13;

//eqn for current across output pins: 
//I = (V*(1k ohm))/(R_s * R_l) where R_s = shunt resistor value and r_l = load resistor value
//however, on default board, R_s = 0.1 ohm and R_l = 10k, so all the resistors cancel out
//I = the voltage reading on the board

//notes (from SparkFun tutorial)
//make sure ground of measurement circuit is connected to ground of INA169 board. 


const int SENSOR_PIN = A1;
const float VREF = 5; ///using internal

float current; //current
int sensorVal;
float voltage;


void setup() {
  // put your setup code here, to run once:
//  pinMode(LED_PIN, OUTPUT);

  Serial.begin(9600); //begin serial connection
  //analogReference(INTERNAL);

}

void loop() {
  // put your main code here, to run repeatedly:

//  digitalWrite(LED_PIN, HIGH);
//  delay(1000);
//  digitalWrite(LED_PIN, LOW);
//  delay(1000);

  //check this with multimeter
  sensorVal = analogRead(SENSOR_PIN);
  //Serial.println(sensorVal);
  voltage = sensorVal * (VREF / 1023.0);
  Serial.println(voltage, 4);
  
//  current = (analogRead(SENSOR_PIN)*V_REF)/1023;
//
//  Serial.print(current, 3);
//  Serial.println(" A");

  // Delay program for a few milliseconds
  delay(500);

}
