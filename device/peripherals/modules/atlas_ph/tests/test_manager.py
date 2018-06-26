# Import standard python libraries
import sys, os, json

# Get current working directory
cwd = os.getcwd()
print("Running test from: {}".format(cwd))

# Set correct import path
if cwd.endswith("atlas_ph"):
    print("Running test locally")
    os.chdir("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running test globally")
else:
    print("Running tests from invalid location")
    sys.exit(0)

# Import manager
from device.peripherals.modules.atlas_ph.manager import AtlasPHManager

# Import device utilities
from device.utilities.modes import Modes

# Import shared memory
from device.state import State

# Import test config
device_config = json.load(open("device/peripherals/modules/atlas_ph/tests/config.json"))
peripheral_config = device_config["peripherals"][0]

# Initialize state
state = State()


def test_init():
    manager = AtlasPHManager(
        name="Test", state=state, config=peripheral_config, simulate=True
    )


def test_initialize():
    manager = AtlasPHManager("Test", state, peripheral_config, simulate=True)
    manager.initialize()
    assert True


def test_setup():
    manager = AtlasPHManager("Test", state, peripheral_config, simulate=True)
    manager.setup()
    assert True


def test_update():
    manager = AtlasPHManager("Test", state, peripheral_config, simulate=True)
    manager.update()
    assert True


def test_reset():
    manager = AtlasPHManager("Test", state, peripheral_config, simulate=True)
    manager.reset()
    assert True


def test_shutdown():
    manager = AtlasPHManager("Test", state, peripheral_config, simulate=True)
    manager.shutdown()
    assert True
