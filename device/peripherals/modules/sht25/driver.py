# Import standard python modules
import time
from typing import NamedTuple, Optional, Tuple

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities import bitwise


class UserRegister(NamedTuple):
    """ Dataclass for parsed user register byte. """
    resolution: int
    end_of_battery: bool
    heater_enabled: bool
    reload_disabled: bool


class SHT25Driver:
    """ Driver for atlas sht25 temperature and humidity sensor. """


    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
            channel: Optional[int] = None, simulate: bool = False) -> None:
        """ Initializes sht25 driver. """

        # Initialize parameters
        self.simulate = simulate

        # Initialize logger
        self.logger = Logger(
            name = "Driver({})".format(name),
            dunder_name = __name__,
        )

        # Initialize I2C
        self.i2c = I2C(
            name = name,
            bus = bus,
            address = address,
            mux = mux,
            channel = channel,
            simulate = simulate,
        )


    def read_temperature(self) -> Tuple[Optional[float], Error]:
        """ Reads temperature value from sensor hardware. """
        self.logger.debug("Reading temperature value from hardware")
        
        # Send read temperature command (no-hold master)
        error = self.i2c.write([0xF3])

        # Check for errors
        if error.exists():
            error.report("Driver unable to read temperature")
            return None, error
            
        # Wait for sensor to process, see datasheet Table 7
        # SHT25 is 12-bit so max temperature processing time is 22ms
        time.sleep(0.22)

        # Read sensor data
        bytes_, error = self.i2c.read(2)

        # Check for errors
        if error.exists():
            error.report("Driver unable to read temperature")
            return None, error

        # Convert temperature data and set significant figures
        msb, lsb = bytes_
        raw = msb * 256 + lsb
        temperature = -46.85 + ((raw * 175.72) / 65536.0)
        temperature = float("{:.0f}".format(temperature))

        # Successfully read temperature!
        self.logger.debug("Temperature: {} C".format(temperature))
        return temperature, Error(None)


    def read_humidity(self) -> Tuple[Optional[float], Error]:
        """ Reads humidity value from sensor hardware. """
        self.logger.debug("Reading humidity value from hardware")

        # Send read humidity command (no-hold master)
        error = self.i2c.write([0xF5])

        # Check for errors
        if error.exists():
            error.report("Driver unable to read humidity")
            return None, error

        # Wait for sensor to process, see datasheet Table 7
        # SHT25 is 12-bit so max humidity processing time is 29ms
        time.sleep(0.29)

        # Read sensor
        bytes_, error = self.i2c.read(2) # Read sensor data

        # Check for errors
        if error.exists():
            error.report("Driver unable to read humidity")
            return None, error

        # Convert humidity data and set significant figures
        msb, lsb = bytes_
        raw = msb * 256 + lsb
        humidity = -6 + ((raw * 125.0) / 65536.0)
        humidity = float("{:.0f}".format(humidity))
        
        # Successfully read humidity!
        self.logger.debug("Humidity: {} %".format(humidity))
        return humidity, Error(None)


    def read_user_register(self) -> Tuple[Optional[UserRegister], Error]: 
        """ Reads user register from sensor hardware. """
        self.logger.debug("Reading user register")

        # Read register
        byte, error = self.i2c.read_register(0xE7)

        # Check for errors
        if error.exists():
            error.report("Driver unable to read user register")
            return None, error

        # Parse register content
        self.logger.debug("byte = 0x{:02X}".format(byte))
        resolution_msb = bitwise.get_bit_from_byte(bit=7, byte=byte)
        resolution_lsb = bitwise.get_bit_from_byte(bit=0, byte=byte)
        user_register = UserRegister(
            resolution = resolution_msb << 1 + resolution_lsb,
            end_of_battery = bool(bitwise.get_bit_from_byte(bit=6, byte=byte)),
            heater_enabled = bool(bitwise.get_bit_from_byte(bit=2, byte=byte)),
            reload_disabled = bool(bitwise.get_bit_from_byte(bit=1, byte=byte)),
        )
        
        # Successfully read user register!
        self.logger.debug("User register: {}".format(user_register))
        return user_register, Error(None)


    def reset(self) -> Error:
        """ Initiates soft reset on sensor hardware. """
        self.logger.info("Initiating soft reset")

        # Send reset command
        error = self.i2c.write([0xFE])

        # Check for errors
        if error.exists():
            error.report("Driver unable to reset")
            return error

        # Successfully reset!
        return Error(None)


