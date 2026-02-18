#ifndef I2C_TOOLS_H
#define I2C_TOOLS_H

#include <stdint.h>

int i2c_bus(const char *bus_path);
int i2c_read_byte(int bus, uint8_t slave_addr, uint8_t register_addr);
int i2c_write_byte(int bus, uint8_t slave_addr, uint8_t register_addr, uint8_t value);

#endif // I2C_TOOLS_H