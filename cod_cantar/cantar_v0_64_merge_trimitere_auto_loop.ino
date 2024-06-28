#define TINY_GSM_MODEM_SIM800
#include <Sim800l.h>
#include "HX711.h"
#include "RTClib.h"
#include <Wire.h>
#include <EEPROM.h>
#include "HardwareSerial.h"
#include <Adafruit_AHT10.h>
#include "STM32LowPower.h"

#include <Adafruit_ST7735.h>
#include <Wire.h>

#include <TinyGsmClient.h>
#include <PubSubClient.h>
#define RTC_SDA_PIN   PA10
#define RTC_SCL_PIN   PA9
#define GSM_POWER_PIN PA4
#define GSM_RST_PIN   PB1

#define VOLT_PIN PA1

#define TEMP_POWER_PIN PB13

#define HX711_POWER_PIN PB8

#define HC05_POWER_PIN PB12

#define CELL_DATA_PIN PB3
#define CELL_CLK_PIN  PA15


#define WEIGHT_ADDR 100

char* text;
char* number = "0774098203";
bool error, firstWeightingFlag = false; //to catch the response of sendSms
char smsTextMessage[160];  // max size of an SMS

const char apn[] = "net";
const char gprsUser[] = "";
const char gprsPass[] = "";

// MQTT details
 
const char* broker = "iotsmarthouse.go.ro";
const char* topicMessage = "/Cantar/Robert/Mesaje";
const char* topicSignal = "/Cantar/Robert/Semnal";
const char* topicMasa = "/Cantar/Robert/Masa";
const char* topicTime = "/Cantar/Robert/Timp";
const char* topicHello = "/Cantar/Robert/Hello";
const char* topicBattery = "/Cantar/Robert/Battery";
const char* topicTemp = "/Cantar/Robert/Temp";
const char* topicHumidity = "/Cantar/Robert/Humidity";
const int port = 1883;

char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};

static uint8_t rtcMinut = 0, nowMinut = 0;
static uint8_t rtcHour = 0;
static uint8_t state = 0;
static uint8_t signalQ = 0;
static uint8_t signalRssi = 0;
static uint32_t lastReconnectAttempt = 0;

static String actualTime = "", subMessage = "";
static boolean rtcSync = false, rapFlag = false, firstWeightFlag = true;
static int yearN = 0, monthN = 0, dayN = 0, hourN = 0, minuteN = 0, secondN = 0;

static float currentWeight = 0, bufferWeight = 0;
char masaTrimisa[20];
double masa;
String masa_str;
int len;
float calibration_factor = -19803.00;
HardwareSerial Serial2(USART2);   
HardwareSerial Serial3(USART3);
Adafruit_AHT10 aht;
Sim800l gsm;
TinyGsm modem(Serial3);
TinyGsmClient client(modem);
PubSubClient mqtt(client);
HX711 scale;
RTC_DS1307 rtc;


void setup() {
  // put your setup code here, to run once:
  pinMode(GSM_POWER_PIN, OUTPUT);
  pinMode(HX711_POWER_PIN, OUTPUT);
  pinMode(HC05_POWER_PIN, OUTPUT); 
  pinMode(GSM_RST_PIN, OUTPUT);
  pinMode(TEMP_POWER_PIN, OUTPUT);
  pinMode(VOLT_PIN, INPUT_ANALOG);
  
  analogReadResolution(12);
  digitalWrite(GSM_POWER_PIN, LOW);
  digitalWrite(HX711_POWER_PIN, LOW);
  digitalWrite(HC05_POWER_PIN, LOW);
  digitalWrite(TEMP_POWER_PIN, LOW);
  hc05PowerOff();
  hx711PowerOn();
  scale.tare();
  delay(1000);
  digitalWrite(GSM_RST_PIN, LOW);
  delay(1000);
  digitalWrite(GSM_RST_PIN, HIGH);
  Serial2.begin(9600);
  Serial2.println("Wait...");

  scale.begin(CELL_DATA_PIN, CELL_CLK_PIN);
  scale.set_scale(calibration_factor);
  tempPowerOn();
  delay(3000);
  if (! aht.begin()) {
    Serial2.println("Could not find AHT10? Check wiring");
    while (1)
      delay(10);
  }
  tempPowerOff();
  Serial2.println("AHT10 found");
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
  hx711PowerOn();

}

void loop() {
  // put your main code here, to run repeatedly:
  switch(state)
  {
    case 0:
    {
      Serial2.println("State = ");
      Serial2.print(state);
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
          //gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
          rtcSync = true;
          
        }
        Serial2.println("GSM signal is poor");
        state = 2;
      }else if(signalQ >= 10 and signalQ <= 14){
        if(!rtcSync){
          //gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
          //rtc.adjust(DateTime(yearN, monthN, dayN, hourN , minuteN, secondN));
          rtcSync = true;
        }
        Serial2.println("GSM signal is OK");
        state = 2;
      }else if(signalQ >= 15 and signalQ <= 19){
        if(!rtcSync){
          //gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
          //rtc.adjust(DateTime(yearN, monthN, dayN, hourN , minuteN, secondN));
          rtcSync = true;
        }
        Serial2.println("GSM signal is good");
        state = 2;
      }else if(signalQ >= 20){
        if(!rtcSync){
          //gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
          //rtc.adjust(DateTime(yearN, monthN, dayN, hourN , minuteN, secondN));
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
      hx711PowerOn();
      delay(2000);
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
      delay(100);
      scale.tare();
      hx711PowerOff();

      tempPowerOn();
      
      if (! aht.begin()) {
        Serial2.println("Could not find AHT10? Check wiring");
        while (1) delay(10);
      }
      sensors_event_t humidity, temp;
      aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
      Serial2.print("Temperature: "); Serial2.print(temp.temperature); Serial2.println(" degrees C");
      Serial2.print("Humidity: "); Serial2.print(humidity.relative_humidity); Serial2.println("% rH");
      tempPowerOff();
      delay(2000);
      state = 3;
    }
    case 3:
    {
      Serial2.println("State = ");
      Serial2.print(state);
      error = gsm.sendSms(number, "Ready for communicaton!");
      if(error){
        modem.gprsConnect(apn, gprsUser, gprsPass);
        delay(4000);
        Serial2.print("Waiting for network...");
        if (!modem.isNetworkConnected()) {
          Serial2.println(" fail");
          delay(10000);
          return;
        }
        Serial2.println(" success");
        if (modem.isNetworkConnected()) {
          Serial2.println("Network connected");
        }
        // MQTT Broker setup
        mqtt.setServer(broker, 1883);
        mqtt.setCallback(mqttCallback);
        state = 4;
      }
      else{
        state = 3;
      }
    }
    //sleep
    case 4:
    {
      Serial2.println();
      Serial2.println("State: ");
      Serial2.print(state);
      if (!mqtt.connected()) {
      Serial2.println("=== MQTT NOT CONNECTED ===");
      // Reconnect every 10 seconds
      uint32_t t = millis();
      if (t - lastReconnectAttempt > 10000L) {
        lastReconnectAttempt = t;
        if (mqttConnect()) {
          Serial2.println("CONNECTED");
          lastReconnectAttempt = 0;
          hx711PowerOn();
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
          hx711PowerOff();
          
          mqtt.publish(topicMasa, (char*)(String(masa)).c_str(),1);
          delay(100);
          gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
          rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
          Serial2.println("RTC sync was made");
          DateTime now = rtc.now();
          String buf = String(now.hour(), DEC);
          buf += ":";
          buf += String(now.minute(), DEC);
          Serial2.println(buf);
          mqtt.publish(topicTime, (char*)buf.c_str(),1);
          delay(1000);
          hx711PowerOn();
          scale.tare();
          Serial2.println("HX reset was made");
          delay(100);
          int val = analogRead(VOLT_PIN);
          float voltage = (float(val)*4.13/3993);
          Serial2.println(voltage);
          String procent = "";
          if(voltage <= 4.20 && voltage >= 3.7)
            procent = "100%";
          if(voltage <= 3.7 && voltage >= 3.4)
            procent = "75%";
          if(voltage <= 3.4 && voltage >= 3)
            procent = "50%";
          if(voltage <= 3 && voltage >= 2.6)
            procent = "25%";
          if(voltage <= 2.6)
            procent = "0%";
          Serial2.println();
          Serial2.println(procent);
          mqtt.publish(topicBattery, procent.c_str(), 1);
          delay(100);
          tempPowerOn();
          sensors_event_t humidity, temp;
          float temperature, hum;
          String tempStr, humStr;
          aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
          Serial2.print("Temperature: ");
          Serial2.print(temp.temperature);
          Serial2.println(" degrees C");
          temperature = temp.temperature;
          hum = humidity.relative_humidity;
          Serial2.print("Humidity: "); Serial2.print(humidity.relative_humidity); Serial2.println("% rH");
          tempStr = (String) temperature;
          humStr = (String) hum;
          mqtt.publish(topicTemp, tempStr.c_str(), 1);
          mqtt.publish(topicHumidity, humStr.c_str(), 1);
          Serial2.println("Data uploaded!");
        }
      }
        delay(1000);
        return;
      }
      for(int i = 0;i <= 1800000; i++)
        mqtt.loop();
    }
    case 5:
    {
      Serial2.println();
      Serial2.print("State: ");
      Serial2.print(state);
      hx711PowerOff(); 
      hc05PowerOff();
      gsmPowerOff();
      LowPower.deepSleep(50000);
      gsmPowerOn();
      delay(5000);
      digitalWrite(GSM_RST_PIN, LOW);
      delay(1000);
      digitalWrite(GSM_RST_PIN, HIGH);
      state = 0;
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
void hx711PowerOn(void)
{
  digitalWrite(HX711_POWER_PIN, LOW);
}
void hx711PowerOff(void)
{
  digitalWrite(HX711_POWER_PIN, HIGH);
}
void hc05PowerOn(void)
{
  digitalWrite(HC05_POWER_PIN, LOW);
}
void hc05PowerOff(void)
{
  digitalWrite(HC05_POWER_PIN, HIGH);
}
void tempPowerOn(void)
{
  digitalWrite(TEMP_POWER_PIN, LOW);
}
void tempPowerOff(void)
{
  digitalWrite(TEMP_POWER_PIN, HIGH);
}
void resetGsm(void){
  delay(1000);
  digitalWrite(GSM_RST_PIN, LOW);
  delay(1000);
  digitalWrite(GSM_RST_PIN, HIGH);
}

boolean mqttConnect() {
  Serial2.print("Connecting to ");
  Serial2.print(broker);

  boolean status = mqtt.connect("Cantar", "baiaMare", "Ares");

  if (status == false) {
    Serial2.println(" fail");
    return false;
  }
  Serial2.println(" success");
  mqtt.publish(topicHello, "Test Cantar started");
  delay(100);
  rapFlag = true;

/**
  delay(100);
  gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  Serial2.println("RTC sync was made");
  DateTime now = rtc.now();
  String buf = String(now.hour(), DEC);
  buf += ":";
  buf += String(now.minute(), DEC);
  Serial2.println(buf);
  mqtt.publish(topicTime, (char*)buf.c_str(),1);
  delay(1000);
  hx711PowerOn();
  scale.tare();
  Serial2.println("HX reset was made");
  delay(100);
  int val = analogRead(VOLT_PIN);
  float voltage = (float(val)*4.13/3993);
  Serial2.println(voltage);
  String procent = "";
  if(voltage <= 4.20 && voltage >= 3.7)
    procent = "100%";
  if(voltage <= 3.7 && voltage >= 3.4)
    procent = "75%";
  if(voltage <= 3.4 && voltage >= 3)
    procent = "50%";
  if(voltage <= 3 && voltage >= 2.6)
    procent = "25%";
  if(voltage <= 2.6)
    procent = "0%";
  Serial2.println();
  Serial2.println(procent);
  mqtt.publish(topicBattery, procent.c_str(), 1);
  delay(100);
  tempPowerOn();
  sensors_event_t humidity, temp;
  float temperature, hum;
  String tempStr, humStr;
  aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
  Serial2.print("Temperature: ");
  Serial2.print(temp.temperature);
  Serial2.println(" degrees C");
  temperature = temp.temperature;
  hum = humidity.relative_humidity;
  Serial2.print("Humidity: "); Serial2.print(humidity.relative_humidity); Serial2.println("% rH");
  tempStr = (String) temperature;
  humStr = (String) hum;
  
  Serial2.println("Data uploaded!");
  mqtt.publish(topicTemp, tempStr.c_str(), 1);
  mqtt.publish(topicHumidity, humStr.c_str(), 1);
  
  tempPowerOff();*/
  mqtt.subscribe("/Cantar/Robert/Mesaje");
  return mqtt.connected();
}

void mqttCallback(char* topic, byte* payload, unsigned int len) {
  subMessage = (char*)payload;
  uint8_t idx_1 = subMessage.indexOf("#");
  String receivedMessage = subMessage.substring(0, idx_1);
  String msg = receivedMessage.substring(0, 4);
  Serial2.print("Message received: ");
  Serial2.println(receivedMessage);
  if(msg =="RAPO" || msg =="RAPORT" || msg == "rapo" || msg == "raport"){ 
    rapFlag = true;
    hx711PowerOn();
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
    hx711PowerOff();
    
    mqtt.publish(topicMasa, (char*)(String(masa)).c_str(),1);
  }else if(msg =="SYNC" || msg =="SYNCe" || msg == "sync"){  
    //syncFlag = true; 
    gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    Serial2.println("RTC sync was made");
    DateTime now = rtc.now();
    String buf = String(now.hour(), DEC);
    buf += ":";
    buf += String(now.minute(), DEC);
    Serial2.println(buf);
    mqtt.publish(topicTime, (char*)buf.c_str(),1);
  }else if(msg =="TARA" || msg =="TARAe" || msg == "tara"){   
    delay(5000);
    hx711PowerOn();
    scale.tare();
    Serial2.println("HX reset was made");
    firstWeightFlag = false;
  }else if(msg == "close" || msg == "clos" || msg == "CLOSE" || msg == "CLOS"){
    Serial2.println("Switching states");
    state = 5;
  }else if(msg == "batt" || msg == "battery" || msg == "bate" || msg == "BATT" || msg == "BATE"){
    int val = analogRead(VOLT_PIN);
    float voltage = (float(val)*4.13/3993); //formulae to convert the ADC value to voltage
    Serial2.println(voltage);
    String procent = "";
    if(voltage <= 4.20 && voltage >= 3.7)
      procent = "100%";
    if(voltage <= 3.7 && voltage >= 3.4)
      procent = "75%";
    if(voltage <= 3.4 && voltage >= 3)
      procent = "50%";
    if(voltage <= 3 && voltage >= 2.6)
      procent = "25%";
    if(voltage <= 2.6)
      procent = "0%";
    Serial2.println();
    Serial2.println(procent);
    mqtt.publish(topicBattery, procent.c_str(), 1);

  }else if(msg == "temp" || msg == "TEMP" || msg == "TEM" || msg == "tem"){
    tempPowerOn();
    sensors_event_t humidity, temp;
    float temperature, hum;
    String tempStr, humStr;
    aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
    Serial2.print("Temperature: ");
    Serial2.print(temp.temperature);
    Serial2.println(" degrees C");
    temperature = temp.temperature;
    hum = humidity.relative_humidity;
    Serial2.print("Humidity: "); Serial2.print(humidity.relative_humidity); Serial2.println("% rH");
    tempStr = (String) temperature;
    humStr = (String) hum;
    
    Serial2.println("Data uploaded!");
    mqtt.publish(topicTemp, tempStr.c_str(), 1);
    mqtt.publish(topicHumidity, humStr.c_str(), 1);
    
    tempPowerOff();

  }else{
    Serial2.println("Message is undefined ..");
  }
}

