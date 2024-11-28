// code for esp-12s to provide sensor data in json format

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include "DHT.h"

// WiFi credentials
const char* ssid = "ssid";
const char* password = "psk";

// DHT Sensor settings
#define DHTPIN 12          // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22     // DHT22 (AM2302), AM2321
DHT dht(DHTPIN, DHTTYPE);

// Create an instance of the server
ESP8266WebServer server(80);

// Temperature and humidity variables
float temperature = 0.0;
float humidity = 0.0;
float getTemperature;
float getHumidity;
unsigned long previousReadDHT = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());

  // Initialize DHT sensor
  dht.begin();

  // Define server routes
  server.on("/", handleRoot);
  server.onNotFound(handleNotFound);

  // Start the server
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {

  // Handle client requests
  server.handleClient();

  // Read DHT sensor data every 2 seconds
  if (millis() - previousReadDHT > 2000) {
    getTemperature = dht.readTemperature();
    getHumidity = dht.readHumidity();

    if (isnan(getTemperature) || isnan(getHumidity)) {
      Serial.println("DHT read error.");
    } else {
      temperature = getTemperature;
      humidity = getHumidity;
    }

    previousReadDHT = millis();
  }

  // Check WiFi connection and reconnect if needed
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost, attempting to reconnect...");
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
      WiFi.begin(ssid, password);
    }
    Serial.println();
    Serial.print("Reconnected! IP address: ");
    Serial.println(WiFi.localIP());
  }
  
}

void handleRoot() {
  // Prepare the JSON response
  String jsonResponse = "{";
  jsonResponse += "\"temperature\":" + String(temperature, 1) + ",";
  jsonResponse += "\"humidity\":" + String(humidity, 1);
  jsonResponse += "}";

  // Send the HTTP response
  server.send(200, "application/json", jsonResponse);

  Serial.println("JSON response sent:");
  Serial.println(jsonResponse);
}

void handleNotFound() {
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";

  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }

  server.send(404, "text/plain", message);
  Serial.println("Client requested unknown resource:");
  Serial.println(message);
}
