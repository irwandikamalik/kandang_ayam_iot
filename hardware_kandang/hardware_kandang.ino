#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <MQ135.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Custom Library
#include "Relay.h"

// buat object relay
Relay relayLampu(14);
Relay relayKipas(27);
Relay relayHumidifier(26);
Relay relayDrink(25);

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
const char* ssid = "plerr.co";
const char* password = "pleerr22";
//MQTT Mosquitto
const char* mqtt_server = "192.168.100.82";

WiFiClient espClient;
PubSubClient client(espClient);

//NTP Timer
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
const long interval = 1000; // 1 Second
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

bool debug = false;

bool setpoint_ready = false;


void setup() {
  Serial.begin(115200);

  //LCD I2C
  Wire.begin(21, 22); // SDA, SCL
  lcd.init();
  lcd.backlight();
  lcd.clear();

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  client.setBufferSize(512);

  //Servo
  servo1.attach(13);
  servo2.attach(12);
  servo3.attach(33);

  // Relay
  relayLampu.begin();
  relayKipas.begin();
  relayHumidifier.begin();
  relayDrink.begin();

  // DHT
  dht.begin();


  Serial.println("Start Looping");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }
  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  unsigned long now = millis();

  //Interval 1 Second
  if (now - lastSend >= interval) {
    lastSend = now;

    // BACA SENSOR
    // suhu = dht.readTemperature();
    // humidity = dht.readHumidity();
    // gas = gasSensor.getPPM();

    //debug
    suhu = 30;
    humidity = 80;
    gas = 1;

    if (isnan(suhu) || isnan(humidity)) {
      Serial.println("Sensor DHT gagal dibaca!");
      return;
    }


    publishSensor(suhu, humidity, gas);


    if (debug) {
    //Debug Data
    Serial.println("====== DATA ======");
    Serial.print("Suhu: "); Serial.println(suhu);
    Serial.print("Humidity: "); Serial.println(humidity);
    Serial.print("Gas: "); Serial.println(gas);
    
    Serial.print("Set_Suhu: "); Serial.println(set_suhu);
    Serial.print("Set_Humidity: "); Serial.println(set_hum);
    Serial.print("Set_Gas: "); Serial.println(set_gas);

    //Tampilan LCD
    lcd.setCursor(0, 0);
    lcd.print("Tampilan LCD");
    }
  }
  // readSerialCommand();
  controllerAuto(suhu, humidity, gas);
}

void callback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<200> doc;
  deserializeJson(doc, payload, length);
  String t = String(topic);

  if (t == "iot/setpoint") {
    if (doc.containsKey("suhu")) set_suhu = doc["suhu"];
    if (doc.containsKey("hum")) set_hum = doc["hum"];
    if (doc.containsKey("gas")) set_gas = doc["gas"];

    Serial.println("Setpoint updated!");
    publishSetpoint();
    return;
  }

  if (t == "iot/control") {

    // AUTO
    if (doc.containsKey("auto")) {
      bool newAuto = doc["auto"];

      if (auto_mode && !newAuto) {
        relayKipas.off();
        relayHumidifier.off();
        relayDrink.off();
        relayLampu.off();
      }

      auto_mode = newAuto;
    }

    // DRINK
    if (!auto_mode && doc.containsKey("drink")) {
      doc["drink"] ? relayDrink.on() : relayDrink.off();
    }

    // FAN
    if (!auto_mode && doc.containsKey("fan")) {
      doc["fan"] ? relayKipas.on() : relayKipas.off();
    }

    // LAMP
    if (doc.containsKey("lamp")) {
      doc["lamp"] ? relayLampu.on() : relayLampu.off();
    }

    // MIST
    if (!auto_mode && doc.containsKey("mist")) {
      doc["mist"] ? relayHumidifier.on() : relayHumidifier.off();
    }

    // FEED
    if (doc.containsKey("feed") && doc["feed"] == true) {
      StartFeeding();
    }

    publishStatus();

    return;
  }
}


void publishSensor(float suhu, float hum, float gas) {

  StaticJsonDocument<200> doc;

  doc["suhu"] = suhu;
  doc["humidity"] = hum;
  doc["gas"] = gas;
  doc["uptime"] = millis() / 1000; 


  char buffer[256];
  serializeJson(doc, buffer);

  client.publish("iot/sensor", buffer);
}

void publishStatus() {
  StaticJsonDocument<200> doc;

  doc["fan"] = relayKipas.getState();
  doc["lamp"] = relayLampu.getState();
  doc["mist"] = relayHumidifier.getState();
  doc["drink"] = relayDrink.getState();
  doc["auto"] = auto_mode;

  char buffer[256];
  serializeJson(doc, buffer);

  // retain biar UI langsung dapet state terakhir
  client.publish("iot/status", buffer, true);
}

void publishSetpoint() {
  StaticJsonDocument<200> doc;

  doc["suhu"] = set_suhu;
  doc["hum"] = set_hum;
  doc["gas"] = set_gas;

  char buffer[256];
  serializeJson(doc, buffer);

  client.publish("iot/setpoint/status", buffer, true); // retain biar UI dapet terakhir
}


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

void controllerAuto(float suhu, float humidity, float gas) {

  if (!auto_mode) return;

  bool changed = false;
  // KONDISI NYALA
  if (gas > set_gas || suhu > set_suhu || humidity < set_hum) {
    if (!relayKipas.getState()) {
      relayKipas.on();
      changed = true;
    }

    if (!relayHumidifier.getState()) {
      relayHumidifier.on();
      changed = true;
    }

    // Serial.println("Dibawah Setpoint, Menyalakan relay.");
  }

  // KONDISI MATI (hysteresis biar stabil)
  else if (gas < set_gas - 0.5 && suhu < set_suhu - 0.5 && humidity > set_hum - 1) {
    if (relayKipas.getState()) {
      relayKipas.off();
      changed = true;
    }

    if (relayHumidifier.getState()) {
      relayHumidifier.off();
      changed = true;
    }
    // Serial.println("Diatas Setpoint, Mematikan relay.");
  }
  if (changed) {
    publishStatus();
  }
}

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  Serial.print("Connecting Wi-Fi...\n");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting MQTT...\n");

    if (client.connect("ESP32Client")) {
      Serial.println("connected");

      // Subscribe and Publish on First Load
      client.subscribe("iot/control");
      client.subscribe("iot/setpoint");
      publishStatus();
      publishSetpoint(); 
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.print("\n");
      delay(2000);
    }
  }
}