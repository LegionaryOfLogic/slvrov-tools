#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>
#include "i2c_tools.h"


int i2c__open_bus(const char *bus_path) {
    int fd = open(bus_path, O_RDWR);
    if (fd < 0) {
        perror("Failed to open I2C bus");
        return -1;
    }

    return fd;
}


int i2c_read_byte(int bus, uint8_t slave_addr, uint8_t register_addr) {
    uint8_t register_value;
    uint8_t local_register_addr = register_addr;

    /*
    Reading from an I2C device typically involves two messages:
    1. Writing the register address to the device to specify which register we want to read
    2. Reading the value from that register
    */

    struct i2c_msg msgs[2];

    // selecting register on slave
    msgs[0].addr  = slave_addr;
    msgs[0].flags = 0;
    msgs[0].len   = 1;
    msgs[0].buf   = &local_register_addr;

    // reading value from slave
    msgs[1].addr  = slave_addr;
    msgs[1].flags = I2C_M_RD;
    msgs[1].len   = 1;
    msgs[1].buf   = &register_value;

    struct i2c_rdwr_ioctl_data read_msgs = {
        .msgs  = msgs,
        .nmsgs = 2
    };

    if (ioctl(bus, I2C_RDWR, &read_msgs) < 0) {
        perror("Failed to read from I2C device");
        return -1;
    }

    return register_value;
}


int i2c_write_byte(int bus, uint8_t slave_addr, uint8_t register_addr, uint8_t value) {
    uint8_t buffer[2] = {register_addr, value};

    /* 
    We could simply buse a single write message, as we are writing both register_addr and value at the same time. 
    However, for consistency with the read_byte function, we also use the i2c_rdwr_ioctl_data structure.
    */

    struct i2c_msg msg;
    msg.addr = slave_addr;
    msg.flags = 0;
    msg.len = sizeof(buffer);
    msg.buf = buffer;

    struct i2c_rdwr_ioctl_data write_msg = {
        .msgs  = &msg,
        .nmsgs = 1
    };

    if (ioctl(bus, I2C_RDWR, &write_msg) < 0) {
        perror("Failed to write to I2C device");
        return -1;
    }

    return 0;
}