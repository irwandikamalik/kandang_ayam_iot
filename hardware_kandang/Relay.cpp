#include "Relay.h"

Relay::Relay(int pin, bool activeLow) {
  this->pin = pin;
  this->activeLow = activeLow;
}

void Relay::begin() {
  pinMode(pin, OUTPUT);
  off(); // default OFF
}

void Relay::on() {
  digitalWrite(pin, activeLow ? LOW : HIGH);
}

void Relay::off() {
  digitalWrite(pin, activeLow ? HIGH : LOW);
}

void Relay::toggle() {
  digitalWrite(pin, !digitalRead(pin));
}

bool Relay::getState() {
  int state = digitalRead(pin);
  return activeLow ? (state == LOW) : (state == HIGH);
}