# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Import sensor module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_ec.sensor import AtlasECSensor
except:
    # ... if running tests from same dir as sensor.py
    os.chdir("../../../../")
    from device.peripherals.modules.atlas_ec.sensor import AtlasECSensor

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug sensor")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser cnfigs
parser.add_argument("--device", type=str, help="specifies device config")

# Setup parser functions
parser.add_argument("-i", "--initialize", action="store_true", help="initialize sensor")
parser.add_argument("-s", "--setup", action="store_true", help="setup sensor")
parser.add_argument("-p", "--probe", action="store_true", help="probe sensor")
parser.add_argument("-r", "--reset", action="store_true", help="reset sensor")
parser.add_argument("-ec", "--read-ec", action="store_true", help="read EC")

# Run main
if __name__ == "__main__":

    # Read in arguments
    args = parser.parse_args()

    # Initialize logger
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.info:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Check for device config
    if args.device != None:
        print("Using device config: {}".format(args.device))
        device_config = json.load(open("data/devices/{}.json".format(args.device)))
        peripheral_config = get_peripheral_config(
            device_config["peripherals"], "AtlasEC-Reservoir"
        )
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Initialize sensor
    sensor = AtlasECSensor(
        name="AtlasEC-Reservoir",
        bus=peripheral_config["parameters"]["communication"]["bus"],
        address=int(peripheral_config["parameters"]["communication"]["address"], 16),
        mux=int(peripheral_config["parameters"]["communication"]["mux"], 16),
        channel=peripheral_config["parameters"]["communication"]["channel"],
    )

    # Check for loop
    if args.loop:
        loop = True
    else:
        loop = False

    # Loop forever
    while True:

        # Check if initializing
        if args.initialize:
            print("Initalizing sensor")
            error = sensor.initialize()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Sensor initialized!")

        # Check if setting up
        if args.setup:
            print("Setting up sensor")
            error = sensor.initialize()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Sensor setup!")

        # Check if probing
        elif args.probe:
            print("Probing sensor")
            error = sensor.probe()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Sensor is active!")

        # Check if resetting
        elif args.reset:
            print("Resetting sensor")
            sensor.reset()
            print("Sensor reset!")

        # Check if reading electrical conductivity
        elif args.read_ec:
            print("Reading EC")
            ec, error = sensor.read_electrical_conductivity()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("EC: {} mS/cm".format(ec))

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
