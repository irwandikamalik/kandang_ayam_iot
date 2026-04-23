#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <MQ135.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <ArduinoJson.h>

// Custom Library
#include "Relay.h"

// buat object relay
Relay relayLampu(14);
Relay relayKipas(27);
Relay relayHumidifier(26);
Relay relay4(25);

//Servo
Servo servo1;
Servo servo2;
Servo servo3;

//test
String inputString = "";
int angle = 0;

//LCD I2C
LiquidCrystal_I2C lcd(0x27, 16, 2);

// WIFI
const char* ssid = "akaii";
const char* password = "akaiakai";

//NTP Timer
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 7 * 3600, 60000);
bool sudahJalan = false; //Flag NTP Timer
const int timerJam = 23;
const int timerMenit = 25;

// DHT22
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// MQ135
#define MQ135_PIN 34
MQ135 gasSensor = MQ135(MQ135_PIN);

// TIMER
unsigned long lastSend = 0;
const long interval = 1 * 1000; // 1 Second
unsigned long lastTimer = 0;
const long intervalTimer = 1 * 10; // 10 MiliSecond

// Timer Beri Pakan
bool is_feeding = false;
unsigned long feeding_start_time = 0;
const unsigned long feeding_duration = 5000; // 5 detik

// State Controller
bool env_state = false; 

// Global Variable Sensor
float suhu = 0;
float humidity = 0;
float gas = 0;

// Global Variable Setpoint
float set_suhu = 30;
float set_hum = 60;
float set_gas = 20;

bool auto_mode = false;

bool debug = true;


void setup() {
  Serial.begin(115200);

  //LCD I2C
  Wire.begin(21, 22); // SDA, SCL
  lcd.init();
  lcd.backlight();
  lcd.clear();

  WiFi.begin(ssid, password);
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  // mulai NTP
  timeClient.begin();

  //Servo
  servo1.attach(13);
  servo2.attach(12);
  servo3.attach(33);

  // Relay
  relayLampu.begin();
  relayKipas.begin();
  relayHumidifier.begin();
  relay4.begin();

  // DHT
  dht.begin();


  Serial.println("Start Looping");
}

void loop() {
  timeClient.update();

  unsigned long now = millis();

  //Interval 1 Second
  if (now - lastSend >= interval) {
    lastSend = now;

    // BACA SENSOR
    suhu = dht.readTemperature();
    humidity = dht.readHumidity();
    gas = gasSensor.getPPM();

    if (isnan(suhu) || isnan(humidity)) {
      Serial.println("Sensor DHT gagal dibaca!");
      return;
    }


    sendSerialData(suhu, humidity, gas);



    if (debug) {
    //Debug Data
    Serial.println("====== DATA ======");
    Serial.print("Suhu: "); Serial.println(suhu);
    Serial.print("Humidity: "); Serial.println(humidity);
    Serial.print("Gas: "); Serial.println(gas);
    
    Serial.print("Set_Suhu: "); Serial.println(set_suhu);
    Serial.print("Set_Humidity: "); Serial.println(set_hum);
    Serial.print("Set_Gas: "); Serial.println(set_gas);
    

    Serial.print("Jam: ");
    Serial.print(timeClient.getHours());
    Serial.print(":");
    Serial.print(timeClient.getMinutes());
    Serial.print(":");
    Serial.println(timeClient.getSeconds());
    }

    //Tampilan LCD
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Tampilan LCD");

    //Run sesuai Jam NTP    
    int jam = timeClient.getHours();
    int menit = timeClient.getMinutes();
    int detik = timeClient.getSeconds();


    if (jam == timerJam && menit == timerMenit && !sudahJalan) {
      Serial.println("Jam 5 sore! Eksekusi...");

      // Run Action
      StartFeeding();
      relayLampu.on();

      sudahJalan = true;
    }

    // reset flag setelah lewat menit 0
    if (menit != timerMenit) {
      sudahJalan = false;
    }
  }

  if (now - lastTimer >= intervalTimer) {
    lastTimer = now;
  
  // //Servo
  // servo1.write(0);
  // servo2.write(0);
  // servo3.write(0);
    // relayLampu.on();
    // relayKipas.on();
    // relayHumidifier.on();
    // relay4.on();


  }

  
  readSerialCommand();
  HandleFeeding();
  controllerAuto(suhu, humidity, gas);

}


/*
**********Cara Menggunakan Relay**********
  relayLampu.on();
  delay(1000);

  relayLampu.off();
  delay(1000);

  relayKipas.toggle();
  delay(1000);

  relayHumidifier.on();
  relay4.on();
  delay(2000);

  relayHumidifier.off();
  relay4.off();
  delay(2000);
*/

void StartFeeding() {
  if (!is_feeding) {
    is_feeding = true;
    feeding_start_time = millis();

    servo1.write(180); // buka
    servo2.write(180); // buka
    servo3.write(180); // buka
    Serial.println("Feeding started");
  }
}

void HandleFeeding() {
  if (is_feeding && millis() - feeding_start_time >= feeding_duration) {
    servo1.write(0); // tutup
    servo2.write(0); // tutup
    servo3.write(0); // tutup
    is_feeding = false;

    Serial.println("Feeding finished");
  }
}

void controllerAuto(float suhu, float humidity, float gas) {

  if (!auto_mode) return;
  // KONDISI NYALA
  // if (!env_state && (gas > set_gas || suhu > set_suhu || humidity > set_hum)) {
  if (gas > set_gas || suhu > set_suhu || humidity > set_hum) {
    relayKipas.on();
    relayHumidifier.on();

    env_state = true;
    Serial.println("AUTO ON");
  }

  // KONDISI MATI (hysteresis biar stabil)
  // else if (env_state && (gas < set_gas - 2 && suhu < set_suhu - 2 && humidity < set_hum - 5)) {
  else if (gas < set_gas - 0.5 && suhu < set_suhu - 0.5 && humidity < set_hum - 1) {
    relayKipas.off();
    relayHumidifier.off();

    env_state = false;
    Serial.println("AUTO OFF");
  }
}

void sendSerialData(float suhu, float humidity, float gas) {
  String json = "{";
  json += "\"suhu\":" + String(suhu, 2) + ",";
  json += "\"humidity\":" + String(humidity, 2) + ",";
  json += "\"gas\":" + String(gas, 2);
  json += "}";

  Serial.println(json);
}


void readSerialCommand() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    Serial.println("RECEIVED: " + input);

    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, input);

    if (error) {
      Serial.println("JSON ERROR");
      return;
    }

    // ======================
    // FEED
    // ======================
    if (doc["feed"] == true) {
      StartFeeding();
    }

    // ======================
    // AUTO
    // ======================
    if (doc.containsKey("auto")) {
      auto_mode = doc["auto"];

    }

    // ======================
    // LAMP
    // ======================
    if (doc.containsKey("lamp")) {
      if (doc["lamp"]) relayLampu.on();
      else relayLampu.off();
    }

    // ======================
    // FAN
    // ======================
    if (doc.containsKey("fan")) {
      if (doc["fan"]) relayKipas.on();
      else relayKipas.off();
    }

    // ======================
    // MIST
    // ======================
    if (doc.containsKey("mist")) {
      if (doc["mist"]) relayHumidifier.on();
      else relayHumidifier.off();
    }
    // ======================
    // SETPOINT
    // ======================
    if (doc.containsKey("set_suhu")) {
      set_suhu = doc["set_suhu"];
    }

    if (doc.containsKey("set_hum")) {
      set_hum = doc["set_hum"];
    }

    if (doc.containsKey("set_gas")) {
      set_gas = doc["set_gas"];
    }
  }
}