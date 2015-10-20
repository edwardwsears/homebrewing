/*
  Edward Sears
  Arduino program to read temperature from probe
  and show on lcd screen

  The circuit:
 * LCD RS pin to digital pin 12
 * LCD Enable pin to digital pin 11
 * LCD D4 pin to digital pin 5
 * LCD D5 pin to digital pin 4
 * LCD D6 pin to digital pin 3
 * LCD D7 pin to digital pin 2
 * LCD R/W pin to ground
 * 10K resistor:
 * ends to +5V and ground
 * wiper to LCD VO pin (pin 3)

 Powerswitchtails
 * port "1: +in"
    * cold: pin 8
    * hot: pin 13
 * port "2: -in" connected to gnd

 */

// include the library code:
#include <LiquidCrystal.h>
#include <OneWire.h>
//#include <TimerOne.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
//initialize temperature probe
int DS18S20_Pin = 7;
OneWire ds(DS18S20_Pin);
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
int set_temp = 0;
int temp_range = 0;
float curr_temp = 0.0;
boolean canCool = false;
boolean canHeat = false;
boolean isCooling = false;
boolean isHeating = false;

//initialize powerswitchtails
int switch_pin_cold = 8;
int switch_pin_hot = 13;

void setup()  {
  // set up the LCD's number of columns and rows: 
  lcd.begin(16, 2);
  Serial.begin(9600);
  serialFlush();
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);

  //setup switch cold
  pinMode(switch_pin_cold,OUTPUT);
  digitalWrite(switch_pin_cold,LOW);
  //setup switch hot
  pinMode(switch_pin_hot,OUTPUT);
  digitalWrite(switch_pin_hot,LOW);

  //removed interrupt, just run in loop
  //Timer1.initialize(500000);         // initialize timer1, and set a 1/2 second period
  //Timer1.attachInterrupt(PID_control);  // attaches PID_control() as a timer overflow interrupt

}

void loop(){
    curr_temp = getTemp();
    set_lcd(curr_temp,set_temp,isCooling,isHeating);

    if (Serial.available()) {
      boolean in_cmd_seq = true;

      while (in_cmd_seq){
        serialEvent(true);

        if (inputString == "setTemp"){
          serialEvent(true);
          set_temp = inputString.toInt();
        }
        else if (inputString == "setRange"){
          serialEvent(true);
          temp_range = inputString.toInt();
        }
        else if (inputString == "setControlType"){
          serialEvent(true);
          if (inputString=="canCool"){
            canCool = true;
            canHeat = false;
          }
          else if (inputString=="canHeat"){
            canCool = false;
            canHeat = true;
          }
          else if (inputString=="dualControl"){
            canCool = true;
            canHeat = true;
          }
        }
        else if (inputString == "sendTemp"){
          //just send temp, no other cmds
          //wait for serial to be ready
          serialEvent(false);
          Serial.println(curr_temp);
          in_cmd_seq = false;
        }
        else if (inputString == "end"){
          in_cmd_seq = false;
        }

      }
    }
    
    PID_control();
    delay(1000*1); //loop every 1 secs
}

void PID_control(){
  //TODO create better algorithm
  if (set_temp!=0 && curr_temp!=0){
      float set_temp_diff = abs(curr_temp - set_temp);
      if (set_temp_diff < temp_range){
        //shut off if hits setpoint
        if (isCooling && curr_temp<set_temp){
          //turn off cool
          digitalWrite(switch_pin_cold,LOW);
          isCooling=false;
        }
        else if (isHeating && curr_temp>set_temp){
          //turn off heat
          digitalWrite(switch_pin_hot,LOW);
          isHeating=false;
        }
      }
      else if (curr_temp>set_temp){
        //too hot, turn on cool
        if (canCool){
          //turn on cool
          digitalWrite(switch_pin_cold,HIGH);
          isCooling=true;
          //turn off heat
          digitalWrite(switch_pin_hot,LOW);
          isHeating=false;
        }
      }
      else if (curr_temp<set_temp){
        //too cold, turn on heat
        if (canHeat){
          //turn on heat
          digitalWrite(switch_pin_hot,HIGH);
          isHeating=true;
          //turn off cold
          digitalWrite(switch_pin_cold,LOW);
          isCooling=false;
        }
      }
    
  }
}

void serialEvent(boolean send_ack) {
  //clear the string
  inputString = "";
  stringComplete = false;

  //serial is expected to arrive when this fn is called
  //wait for serial to become available if not yet ready
  while (Serial.available() == 0) {
    delay(1000*1); //wait 1 sec
  }
  while (stringComplete==false) {
    // get the new byte:
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      // if the incoming character is a newline, set a flag
      // so the main loop can do something about it:
      stringComplete = true;
    }
    else {
      // add it to the inputString:
      inputString += inChar;
    }
    
  }
  
  if (send_ack){
     Serial.println("ack");
  }
}

float getTemp(){
  //returns temperature from DS18S20
  byte data[12];
  byte addr[8];
  
  if (!ds.search(addr)){
    //no more sensors on chain, reset search
    ds.reset_search();
    return 1;
  }

  if ( OneWire::crc8( addr, 7) != addr[7]) {
    Serial.println("CRC is not valid!");
    return 1;
  }

  if ( addr[0] != 0x10 && addr[0] != 0x28) {
    Serial.print("Device is not recognized");
    return 1;
  }

  ds.reset();
  ds.select(addr);
  ds.write(0x44,1); // start conversion, with parasite power on at the end

  delay(1000);
  byte present = ds.reset();
  ds.select(addr);  
  ds.write(0xBE); // Read Scratchpad

  for (int i = 0; i < 9; i++) { // we need 9 bytes
    data[i] = ds.read();
  }
  
  ds.reset_search();
  
  byte MSB = data[1];
  byte LSB = data[0];

  float tempRead = ((MSB << 8) | LSB); //using two's compliment
  float TemperatureSumC = ((6*tempRead) + (tempRead/4))/100;
  float TemperatureSum = (TemperatureSumC * (1.8)) +32;
  
  return TemperatureSum;
}

void set_lcd(float curr_temp,int set_temp,boolean isCooling,boolean isHeating){
    lcd.setCursor(0, 0);
    lcd.print(curr_temp);
    lcd.print(" Set: ");
    lcd.print(set_temp);
    lcd.setCursor(0, 1);
    if (isCooling){
      lcd.print("         ");
      lcd.setCursor(0, 1);
      lcd.print("Cool On");
    }
    else if (isHeating){
      lcd.print("         ");
      lcd.setCursor(0, 1);
      lcd.print("Heat On");
    }
    else{
      lcd.print("         ");
      lcd.setCursor(0, 1);
      lcd.print("Both Off");
    }
    //lcd.setCursor(12, 0);
    //lcd.setCursor(12, 1);
    //lcd.print("until high tide");
    //lcd.scrollDisplayLeft();
}

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}
