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
 
 */

// include the library code:
#include <LiquidCrystal.h>
#include <OneWire.h>
// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
//initialize temperature probe
int DS18S20_Pin = 7;
OneWire ds(DS18S20_Pin);
char ch;

//initialize powerswitchtail
int switch_pin = 8;

void setup()  {
  // set up the LCD's number of columns and rows: 
  lcd.begin(16, 2);
  Serial.begin(9600);

  //setup switch
  pinMode(switch_pin,OUTPUT);
  digitalWrite(switch_pin,LOW);
}

void loop(){
    float curr_temp = getTemp();
    set_lcd(curr_temp);
    
   if (Serial.available()){

     ch = Serial.read();

     if ( ch == '1' ) { 
       Serial.println(curr_temp);
     }
     else if ( ch == '2' ){
       //turn on switch
       digitalWrite(switch_pin,HIGH);
     }
     else if ( ch == '3' ){
       //turn off switch
       digitalWrite(switch_pin,LOW);
     }
     else {
       delay(10);
     }
   }
   
    
    delay(1000*10); //loop every 10 secs
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

void set_lcd(float curr_temp){
    lcd.setCursor(0, 0);
    lcd.print("Temperature is:");
    lcd.setCursor(0, 1);
    lcd.print(curr_temp);
    lcd.setCursor(6, 1);
    lcd.print("F");
    //lcd.setCursor(12, 0);
    //lcd.setCursor(12, 1);
    //lcd.print("until high tide");
    //lcd.scrollDisplayLeft();
}
