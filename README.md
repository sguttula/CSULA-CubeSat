# CSULA-CubeSat

### Code for CubeSat motion control

Consists of the following classes.

* __class__ Satellite. A class for satellites in general.

    * __class__ CubeSat(Satellite). A subclass of Satellite for CubeSat.

        * __class__ ImpairedCubeSat(CubeSat). A subclass of CubeSat for a CubeSat that can't rotate and move directionally at the same time.

    * __class__ Target(Satellite).  A subclass of Satellite for the Target.

* __class__ Sim. The simulation infrastructure.

## New Raspberry Pi Set-Up

```
sudo apt-get update
```
Enable interfaces
```
sudo raspi-config
```
Enable Interface options VNC, I2C, SPI, Serial, etc.

(Optional) Install Remote Desktop
```
apt-get install xrdp
```
We also want to install some CircuitPython Adafruit libraries, since we're gonna use a lot of sensors from Adafruit, because they make their own drivers for them.
Follow the instructions here:
https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi

### ``Data`` Dictionary

#### Arrays

Each data array is produced by the simulation by sampling the given variable at specific times and appending them to the save array. For example, position is three-dimensional (x, y, z) and so at each time t is described by a list of length 3. If the simulation samples each variable 1876 times, the final position array will be (3 x 1876), describing the 3D position at each sampled time.

| Variable | Description | Dimensions | Units |
| - | - | - | - |
| ``Time`` | The time at each sample, eg. ``[0.00, 0.04, 0.08, ..., 75.00]`` | 1 | seconds |
| ``Pos `` | The position, where (0, 0, 0) is the starting point on the Earth below the satellite | 3 (x, y, z) | metre |
| ``Vel`` | The velocity in each 3D direction | 3 (xdot, ydot, zdot) | metre/sec |
| ``Att`` | The attitude (or orientation) around each 3D axis | 3 (roll, pitch, yaw) | radian |
| ``AngVel`` | The angular velocity around each 3D axis | 3 (roll vel, pitch vel, yaw vel) | radian/sec |
| ``Inputs`` | The attitude commands around each 3D axis, i.e. the satellite should rotate so that the attitude matches these values. | 3 (roll, pitch, yaw) | radian |
| ``Target pos`` | The point on the ground which any of the shown beams are intersecting, i.e. the target. | 3 (x, y, z) | metre |
| ``ADCS mode`` | The number describing the current mode of the guidance system, where the modes have names given in ``ADCS mode names``. | 1 | - |
| ``Payload mode`` | The number describing the current mode of the payload, where the modes have names given in ``Payload mode names``. The payload mode affects what beams are active within the simulation. | 1 | - |
| ``Payload temp`` | The temperature of the payload. | 1 | deg C |
| ``Energy`` | The energy level of the satellite. | 1 | Joules |

#### Fixed Properties

These variables are produced by the simulation as it runs but otherwise do not change with time.

| Property | Description | Units |
| - | - | - |
| ``Time step`` | The change in time between simulation step. | sec |
| ``Target info`` | Dictionary describing the position and visibility of each target receiver. | - |
| ``ADCS mode names`` | The names of each guidance system mode, where the index of the tuple is used to relate the name to the modes described by the ``ADCS mode`` array. | - |
| ``Payload mode names`` | The names of each payload mode, where the index of the tuple is used to relate the name to the modes described by the ``Payload mode`` array. | - |

### ``Props`` Dictionary

| Key | Description |
| - | - |
| ``Sat`` | Satellite properties, such as mass, geometry, altitude. |
| ``Camera`` | Properties of one or more onboard cameras, such as position on sat body, resolution, pitch angle, field of view. Each camera has its own dictionary. |
| ``Earth`` | Earth properties, such as mass, radius and the resolution (m/px) of the full-size texture image. |
| ``Universal`` | Universal properties describing the laws of physics |
| ``Imagery`` | Info on textures used in simulation and visualisation |
| ``Laser`` | Positions of each laser emitter on the satellite body |



