#define TINY_GSM_MODEM_SIM800
#include <Sim800l.h>
#include "HX711.h"
#include "RTClib.h"
#include <Wire.h>
#include <EEPROM.h>
#include "HardwareSerial.h"

#include <TinyGsmClient.h>
#include <PubSubClient.h>
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
const int port = 1883;

static uint8_t rtcMinut = 0, nowMinut = 0;
static uint8_t rtcHour = 0;
static uint8_t state = 0;
static uint8_t signalQ = 0;
static uint8_t signalRssi = 0;
static uint32_t lastReconnectAttempt = 0;

static String actualTime = "", subMessage = "";
static boolean rtcSync = false, rapFlag = false;
static int yearN = 0, monthN = 0, dayN = 0, hourN = 0, minuteN = 0, secondN = 0;
char masaTrimisa[20];
double masa;
String masa_str;
int len;
float calibration_factor = -19803.00;
HardwareSerial Serial2(USART2);   
HardwareSerial Serial3(USART3);
Sim800l gsm;
TinyGsm modem(Serial3);
TinyGsmClient client(modem);
PubSubClient mqtt(client);
HX711 scale;
RTC_DS1307 rtc;



void mqttCallback(char* topic, byte* payload, unsigned int len) {
  subMessage = (char*)payload;
  uint8_t idx_1 = subMessage.indexOf("#");
  String receivedMessage = subMessage.substring(0, idx_1);
  Serial2.print("Message received: ");
  Serial2.println(receivedMessage);
  if(receivedMessage=="RAPORT" || receivedMessage=="RAPORTe" || receivedMessage=="RAPORT Cantar started"){ 
    rapFlag = true;
    mqtt.publish(topicMasa, (char*)(String(masa)).c_str(),1);
    Serial2.println("Message published: masa");
  }else if(receivedMessage=="SYNC" || receivedMessage=="SYNCe"){  
    //syncFlag = true; 
    gsm.RTCtime(&dayN,&monthN,&yearN,&hourN,&minuteN,&secondN);
    rtc.adjust(DateTime(yearN, monthN, dayN, hourN , minuteN, secondN));
    Serial2.println("RTC sync was made");
    DateTime now = rtc.now();
    String buf = String(now.hour(), DEC);
    buf += ":";
    buf += String(now.minute(), DEC);
    Serial2.println(buf);
    mqtt.publish(topicTime, (char*)buf.c_str(),1);
  }else if(receivedMessage=="TARA" || receivedMessage=="TARAe"){   
    delay(5000);
    scale.tare();
    Serial2.println("HX reset was made");
  }else{
    Serial2.println("Message is undefined ..");
  }
}

/*void mqttCallback(char* topic, byte* payload, unsigned int len) {
  subMessage = (char*)payload;
  uint8_t idx_1 = subMessage.indexOf("#");
  String receivedMessage = subMessage.substring(0, idx_1);
  Serial2.print("Message arrived [");
  Serial2.print(topic);
  Serial2.print("]: ");
  Serial2.write(payload, len);
  Serial2.println();
  if(receivedMessage == "TARA"){
    scale.begin(CELL_DATA_PIN, CELL_CLK_PIN);
    scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch
    scale.tare();
    Serial2.println("tara");
  }
}
*/
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
  scale.set_scale(calibration_factor);
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
      delay(3000);
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
      state = 3;
    }
    /**case 4:
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
    }*/
    case 3:
    {
      Serial2.println("State = ");
      Serial2.print(state);
      String modemInfo = modem.getModemInfo();
      Serial2.println("Modem Info: ");
      Serial2.print(modemInfo);
      modem.gprsConnect(apn, gprsUser, gprsPass);
      delay(6000);
      Serial2.print("Waiting for network...");
      if (!modem.waitForNetwork()) {
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
    case 4:
    {
      if (!mqtt.connected()) {
      Serial2.println("=== MQTT NOT CONNECTED ===");
      // Reconnect every 10 seconds
      uint32_t t = millis();
      if (t - lastReconnectAttempt > 10000L) {
        lastReconnectAttempt = t;
        if (mqttConnect()) {
          Serial2.println("CONNECTED");
          lastReconnectAttempt = 0;
        }
      }
        delay(1000);
        return;
      }
      for(int i=0; i<=900000; i++)
        mqtt.loop();
      state = 5;
    }
    case 5:
    {
      Serial2.println(state);
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
/*boolean mqttConnect() {
  Serial2.print("Connecting to ");
  Serial2.print(broker);

  boolean status = mqtt.connect("Cantar", "baiaMare", "Ares");

  if (status == false) {
    Serial2.println(" fail");
    return false;
  }
  Serial2.println(" success");
  mqtt.publish(topicHello, "Test Cantar started");
  mqtt.subscribe("/Cantar/Robert/Mesaje");
  return mqtt.connected();
}
*/
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
  mqtt.subscribe("/Cantar/Robert/Mesaje");
  return mqtt.connected();
}



