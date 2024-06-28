#include <STM32LowPower.h>
#define TINY_GSM_MODEM_SIM800
#include <Sim800l.h>
#include "HX711.h"
#include "RTClib.h"
#include <Wire.h>
#include <EEPROM.h>
#include "HardwareSerial.h"

#define RTC_SDA_PIN   PA10
#define RTC_SCL_PIN   PA9
#define GSM_POWER_PIN PA4
#define GSM_RST_PIN   PB1

#define CELL_DATA_PIN PB3
#define CELL_CLK_PIN  PA15

char* text;
char* number = "0774098203";
bool error, firstWeightingFlag = false; //to catch the response of sendSms
char smsTextMessage[160];  // max size of an SMS
static uint8_t rtcMinut = 0, nowMinut = 0;
static uint8_t rtcHour = 0;
static uint8_t state = 0;
static uint8_t signalQ = 0;
static uint8_t signalRssi = 0;
static boolean rtcSync = false;
static int yearN = 0, monthN = 0, dayN = 0, hourN = 0, minuteN = 0, secondN = 0;
char masaTrimisa[20];
double masa;
String masa_str;
int len;
float calibration_factor = -19803.00;
HardwareSerial Serial2(USART2);   
HardwareSerial Serial3(USART3);
Sim800l gsm;
HX711 scale;
RTC_DS1307 rtc;

void setup() {
  // put your setup code here, to run once:
  pinMode(GSM_POWER_PIN, OUTPUT); 
  pinMode(GSM_RST_PIN, OUTPUT);
  digitalWrite(GSM_POWER_PIN, LOW);
  delay(1000);
  digitalWrite(GSM_RST_PIN, HIGH);
  Serial2.begin(9600);
  Serial2.println("Wait...");

  scale.begin(CELL_DATA_PIN, CELL_CLK_PIN);
  scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch
  scale.tare(); //Assuming there is no weight on the scale at start up, reset the scale to 0\\
  delay(3000);

  Serial3.begin(9600);
  gsmPowerOn();
  delay(5000);
  gsm.begin();
  //syncronyze the RTC 
  Wire.begin();
  rtc.begin();
  //trimite sms
  delay(5000);
  Serial2.println("GSM config");
  delay(500);

}

void loop() {
  // put your main code here, to run repeatedly:
  switch(state)
  {
    case 0:
    {
      Serial2.println("State = ");
      Serial2.print(state);
      gsmPowerOn();
      if(gsm.checkModem()){
        state = 1;
        Serial2.println("GSM Modem OK !");
        
      }
      else{
        state = 0;  
        Serial2.println("Waiting for GSM ...");
        delay(2000);
      }
    }

    case 1:
    {
      Serial2.print("State = ");
      Serial2.println(state);
      delay(5000);
      signalQ = gsm.signalQuality();
      signalRssi = 113 - 2*signalQ;
      if(signalQ < 2){
        Serial2.println("GSM signal is missing");
        state = 0;
      }else if(signalQ >= 2 and signalQ <= 9){
        if(!rtcSync){
          gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
          rtcSync = true;
          
        }
        Serial2.println("GSM signal is poor");
        state = 2;
      }else if(signalQ >= 10 and signalQ <= 14){
        if(!rtcSync){
          gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
          rtc.adjust(DateTime(yearN, monthN, dayN, hourN , minuteN, secondN));
          rtcSync = true;
        }
        Serial2.println("GSM signal is OK");
        state = 2;
      }else if(signalQ >= 15 and signalQ <= 19){
        if(!rtcSync){
          gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
          rtc.adjust(DateTime(yearN, monthN, dayN, hourN , minuteN, secondN));
          rtcSync = true;
        }
        Serial2.println("GSM signal is good");
        state = 2;
      }else if(signalQ >= 20){
        if(!rtcSync){
          gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
          rtc.adjust(DateTime(yearN, monthN, dayN, hourN , minuteN, secondN));
          rtcSync = true;
        }
        Serial2.println("GSM signal is excellent");
        state = 2;
      }
      
    }
    case 2:
    {
      Serial2.print("\n");
      Serial2.print("State = ");
      Serial2.print(state);
      Serial2.print("\n");
      Serial2.println("Entering in deepsleep ..........");
      gsmPowerOff();
      LowPower.deepSleep(10000);
       state = 3;
    }
    case 3:
    {
      Serial2.print("\n");
      Serial2.print("State = ");
      Serial2.print(state);
      scale.begin(CELL_DATA_PIN, CELL_CLK_PIN);
      scale.set_scale();
      //scale.tare(); //Reset the scale to 0

      long zero_factor = scale.read_average();
      Serial2.print("\n"); //Get a baseline reading
      Serial2.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
      Serial2.print(zero_factor);
      scale.set_scale(calibration_factor); //Adjust to this calibration facto
      Serial2.print("\n");
      Serial2.print("Reading: ");
      masa = scale.get_units(10);
      Serial2.print(masa);
      masa_str = String(masa);
      masa_str.toCharArray(masaTrimisa, masa_str.length());


      delay(2000);
      state = 4;
    }
    case 4:
    {
      Serial2.println("\n");
      Serial2.print("State = ");
      Serial2.print(state);
      Serial2.println("\n");
      Serial2.println("Awake");
      gsmPowerOn();
      delay(2000);
      digitalWrite(GSM_RST_PIN, LOW);
      delay(10000);
      error = gsm.sendSms(number, masaTrimisa);
      if(error)
      {
        Serial2.println("SMS was sent");
        state = 5;
      }
      else
      {
        Serial2.println("SMS was not sent");
        state = 0;
      }
    }
  }
}

void gsmPowerOn(void){
  digitalWrite(GSM_POWER_PIN, LOW);
  delay(100);
}
void gsmPowerOff(void){
  digitalWrite(GSM_POWER_PIN, HIGH);
  delay(100);
}
