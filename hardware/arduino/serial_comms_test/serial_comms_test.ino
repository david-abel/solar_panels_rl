//testing two-way serial communication w/computer. 


void setup() {
  Serial.begin(9600);
  
}

String rcv;

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available()){
    rcv = Serial.readString();
    Serial.print("RECIEVED ");
    Serial.println(rcv); 
  }

}
