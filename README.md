# sky_power_testing_automation
An automation script, written to perform power tests on the four main Sky Q Set Top Boxes, setup in an automation rack I built.

The script is written to log power on four different types of set top boxes (platforms) called the Titan, Xwing, D1 and V2, implementing different conditions depending on each test. Some conditions are implemented via the Electronic Programmable Guide (EPG): changing the power mode (Eco, Active or None), enabling/disabling the tuners on the box and enabling/disabling the 2.4GHz and 5GHz wireless ports. This is performed using the sky-remote.js module to emulate the remote control (from https://github.com/dalhundal/sky-remote)

The physical conditions that can be changed are: connecting/disconnecting the satellite feeds and connecting/disconnecting ethernet internet connection. The satellite feeds are controlled using a Raspberry Pi's GPIO connected to RF switches (HMC849a). The ethernet connection to the STBs comes from a five port network switch. This switch is powered by a smart plug. By turning the smart plug off, the wired internet connection to the STB is broken.

Power tests are an amalgamation of these conditions. Each test implements a selection of the stated functionallity in a different sequence, in order to ensure that all laws concerning e-products' power consumption are followed. A block diagram of the rack is included in the repository.

The program measures power using "power bricks". Power is retrieved via the "GET ALL" telnet command.

The sky.py file contains the classes and the power_tests.py file contain the tests
