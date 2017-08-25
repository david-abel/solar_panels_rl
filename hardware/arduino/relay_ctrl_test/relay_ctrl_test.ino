


void setup() {
  // put your setup code here, to run once:

  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT); //
  digitalWrite(7, HIGH); //relay is off when pin is low
  digitalWrite(8, HIGH);

}

void loop() {
  // put your main code here, to run repeatedly:

  digitalWrite(7, LOW);
  delay(5000); 
  digitalWrite(7, HIGH);
  delay(10);
  digitalWrite(8, LOW);
  delay(5000);
  digitalWrite(8, HIGH);
  delay(10);

  

}
