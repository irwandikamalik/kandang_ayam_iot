#ifndef RELAY_H
#define RELAY_H

#include <Arduino.h>

class Relay {
  private:
    int pin;
    bool activeLow;

  public:
    // constructor
    Relay(int pin, bool activeLow = true);

    // fungsi kontrol
    void begin();
    void on();
    void off();
    void toggle();
    bool getState();
};

#endif