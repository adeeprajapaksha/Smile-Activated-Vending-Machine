void setup() {
  Serial.begin(9600);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();

    Serial.print("Received command: ");
    Serial.println(command);

    if (command == 'H') {
      // Turn on both motors
      digitalWrite(2, HIGH);
      digitalWrite(3, LOW);
      digitalWrite(4, HIGH);
      digitalWrite(5, LOW);
      delay(500);  // Small delay after turning on motors
      

    } else if (command == 'L') {
      // Turn off both motors (add any additional actions if needed)
      digitalWrite(2, LOW);
      digitalWrite(3, LOW);
      digitalWrite(4, LOW);
      digitalWrite(5, LOW);
      // No additional delay for 'L'
    }
  }
}
