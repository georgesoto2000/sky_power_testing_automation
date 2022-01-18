# sky_power_testing_automation
An automation script, written to perform power tests on the four main Sky Q Set Top Boxes, setup in an automation rack I built.

The script is written to log power on four different types of set top boxes (platforms) called the Titan, Xwing, D1 and V2, implememnting different conditions depending on each test. Some conditions are implemented via the Electronic Programmable Guide (EPG): changing the power mode (Eco, Active or None), enabling/disabling the tuners on the box, enabling/disabling the 2.4GHz and 5GHz wireless ports. This is performed using the sky-remote Node.js module to emulate the remote control.

The physical conditions that can be changed are: connecting/disconnecting the satellite feeds and connecting/disconnecting satellite feeds. The satellite feeds are controlled using a Raspberry Pi's GPIO connected to RF switches (HMC849a). The ethernet connection to the STBs comes from a five port network switch. This switch is powered by a smart plug. By turning the smart plug off, the wired internet connection to the STB is broken.

Power tests are an amalgamation of these conditions. Each test implements a selection of the stated functionallity in a different sequence, in order to ensure that all laws concerning e-products' power consumption are followed. 
