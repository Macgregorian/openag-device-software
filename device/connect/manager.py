# Import python modules
import logging
import threading
import time
import platform
from device.connect.utilities import ConnectUtilities


class ConnectManager:
    """ Sets up and manages internet and IoT connections. """

    # Initialize logger
    extra = {"console_name": "ConnectManager", "file_name": "connect"}
    logger = logging.getLogger("connect")
    logger = logging.LoggerAdapter(logger, extra)

    # Place holder for thread object.
    thread = None

    # ------------------------------------------------------------------------
    def __init__(self, state, ref_iot_manager):
        """Initializes connect manager."""
        self.logger.debug("Initializing manager")

        # Initialize our state
        self.state = state
        self.error = None
        self.status = "Initializing..."
        self.ref_iot_manager = ref_iot_manager
        self.update()
        self._stop_event = threading.Event()  # so we can stop this thread

        # this never changes, so only get once
        self.state.connect["is_bbb"] = ConnectUtilities.is_bbb()

        # initialize this
        self.state.connect["device_UI"] = ConnectUtilities.get_remote_UI_URL()

    # ------------------------------------------------------------------------
    @property
    def error(self):
        """ Gets error value. """
        return self._error

    @error.setter
    def error(self, value):
        """ Safely updates shared state. """
        self._error = value
        with threading.Lock():
            self.state.connect["error"] = value

    # ------------------------------------------------------------------------
    @property
    def status(self):
        """ Gets status value. """
        return self._status

    @status.setter
    def status(self, value):
        """ Safely updates shared state. """
        self._status = value
        with threading.Lock():
            self.state.connect["status"] = value

    # ------------------------------------------------------------------------
    def spawn(self):
        self.logger.info("Spawning connect manager thread")
        self.thread = threading.Thread(target=self.thread_proc)
        self.thread.daemon = True
        self.thread.start()

    # ------------------------------------------------------------------------
    def stop(self):
        self.logger.info("Stopping connect manager thread")
        self._stop_event.set()

    # ------------------------------------------------------------------------
    def stopped(self):
        return self._stop_event.is_set()

    # ------------------------------------------------------------------------
    def thread_proc(self):
        while True:
            if self.stopped():
                break
            self.update()
            if ConnectUtilities.valid_internet_connection():
                time.sleep(300)  # idle for 5 min
            else:
                time.sleep(5)  # fast idle until we get connected

    # ------------------------------------------------------------------------
    def update(self):
        # these may change, so get new values every loop
        self.state.connect[
            "valid_internet_connection"
        ] = ConnectUtilities.valid_internet_connection()
        self.state.connect["is_wifi_bbb"] = ConnectUtilities.is_wifi_bbb()
        self.state.connect["wifis"] = ConnectUtilities.get_wifis()
        self.state.connect["IP"] = ConnectUtilities.get_IP()
        self.state.connect[
            "is_registered_with_IoT"
        ] = ConnectUtilities.is_registered_with_iot()
        self.state.connect["device_id"] = ConnectUtilities.get_device_id()
        self.state.connect["iot_connection"] = self.state.iot[
            "connected"
        ]  # the IoTManager already does this

        if ConnectUtilities.valid_internet_connection():
            self.status = "Connected"
        else:
            self.status = "Not Connected"


#################### REFERENCE FOR TYPE CHECK BRANCH #################################

# # Import standard python modules
# import logging, threading, time, platform

# # Import python types
# from typing import Dict

# # Import device utilities
# from device.utilities import logger, accessors, constants
# from device.utilities.statemachine import manager, modes
# from device.state.main import State

# # Import device managers
# from device.iot.manager import IoTManager

# # Import manager elements
# from device.connect import utilities


# class ConnectManager(manager.StateMachineManager):
#     """ Sets up and manages internet and IoT connections. """

#     _connected: bool = False

#     def __init__(self, state: State) -> None:
#         """Initializes connect manager."""

#         # Initialize parent class
#         super().__init__()

#         # Initialize parameters
#         self.state = state

#         # Initialize logger
#         self.logger = logger.Logger("Connect", "connect")
#         self.logger.debug("Initializing manager")

#         # Initialize reported metrics
#         self.error = None
#         self.status = None
#         self.is_bbb = utilities.is_bbb()
#         self.is_wifi_bbb = utilities.is_wifi_bbb()
#         self.remote_ui_url = utilities.get_remote_ui_url()

#         # Initialize state machine transitions
#         self.transitions: Dict[str, List[str]] = {
#             modes.NORMAL: [modes.SHUTDOWN, modes.ERROR], modes.ERROR: [modes.SHUTDOWN]
#         }
#         # Initialize state machine mode
#         self.mode = modes.NORMAL

#     @property
#     def status(self) -> str:
#         """Gets value."""
#         return self.state.connect.get("status")  # type: ignore

#     @status.setter
#     def status(self, value: str) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["status"] = value

#     @property
#     def error(self):
#         """Gets value."""
#         return self.state.connect.get("error")  # type: ignore

#     @error.setter
#     def error(self, value: str) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["error"] = value

#     @property
#     def is_bbb(self) -> bool:
#         """Gets value."""
#         return self.state.connect.get("is_bbb")  # type: ignore

#     @is_bbb.setter
#     def is_bbb(self, value: bool) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["is_bbb"] = value

#     @property
#     def is_wifi_bbb(self) -> bool:
#         """Gets value."""
#         return self.state.connect.get("is_wifi_bbb")  # type: ignore

#     @is_wifi_bbb.setter
#     def is_wifi_bbb(self, value: bool) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["is_wifi_bbb"] = value

#     @property
#     def remote_ui_url(self) -> str:
#         """Gets value."""
#         return self.state.connect.get("device_UI")  # type: ignore

#     @remote_ui_url.setter
#     def remote_ui_url(self, value: str) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["device_UI"] = value

#     @property
#     def ip(self) -> bool:
#         """Gets value."""
#         return self.state.connect.get("IP")  # type: ignore

#     @ip.setter
#     def ip(self, value: bool) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["IP"] = value

#     @property
#     def wifis(self) -> bool:
#         """Gets value."""
#         return self.state.connect.get("wifis")  # type: ignore

#     @wifis.setter
#     def wifis(self, value: bool) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["wifis"] = value

#     @property
#     def is_iot_registered(self) -> bool:
#         """Gets value."""
#         return self.state.connect.get("is_registered_with_IoT")  # type: ignore

#     @is_iot_registered.setter
#     def is_iot_registered(self, value: bool) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["is_registered_with_IoT"] = value

#     @property
#     def device_id(self) -> str:
#         """Gets value."""
#         return self.state.connect.get("device_id")  # type: ignore

#     @device_id.setter
#     def device_id(self, value: str) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["device_id"] = value

#     @property
#     def iot_connection(self) -> bool:
#         """Gets value."""
#         return self.state.connect.get("iot_connection")  # type: ignore

#     @iot_connection.setter
#     def iot_connection(self, value: bool) -> None:
#         """Safely updates value in shared state."""
#         with self.state.lock:
#             self.state.connect["iot_connection"] = value

#     @property
#     def connected(self) -> bool:
#         """Gets connection status."""
#         return self.state.connect.get("valid_internet_connection", False)

#     @connected.setter
#     def connected(self, value: bool) -> None:
#         """Sets connection status, updates reconnection status, and logs changes."""

#         # Set previous and current connection state
#         prev_connected = self._connected
#         self._connected = value

#         # Check for new connection
#         if prev_connected != self._connected and self._connected:
#             self.logger.info("Connected to internet")
#             self.reconnected = True

#         # Check for new disconnection
#         elif prev_connected != self._connected and not self._connected:
#             self.logger.info("Disconnected from internet")
#             self.reconnected = False

#         # No change to connection
#         else:
#             self.reconnected = False

#         # Update connection status in shared state
#         with self.state.lock:
#             self.state.resource["valid_internet_connection"] = value

#     ##### STATE MACHINE FUNCTIONS ######################################################

#     def run(self) -> None:
#         """Runs state machine."""

#         # Loop forever
#         while True:

#             # Check if manager is shutdown
#             if self.is_shutdown:
#                 break

#             # Check for mode transitions
#             if self.mode == modes.NORMAL:
#                 self.run_normal_mode()
#             elif self.mode == modes.ERROR:
#                 self.run_error_mode()  # defined in parent classs
#             elif self.mode == modes.SHUTDOWN:
#                 self.run_shutdown_mode()  # defined in parent class
#             else:
#                 self.logger.critical("Invalid state machine mode")
#                 self.mode = modes.INVALID
#                 self.is_shutdown = True
#                 break

#     def run_normal_mode(self) -> None:
#         """Runs normal mode."""

#         # Initialize last update time
#         last_update_time = 0.0

#         # Loop forever
#         while True:

#             # Set resource update interval
#             if not self.connected:
#                 update_interval = 5  # seconds
#             else:
#                 update_interval = 300  # seconds -> 5 minutes

#             # Update connection and storage state every update interval
#             if time.time() - last_update_time > update_interval:
#                 last_update_time = time.time()
#                 self.update_connection()

#             # Check for events
#             self.check_events()

#             # Check for transitions
#             if self.new_transition(modes.NORMAL):
#                 break

#             # Update every 100ms
#             time.sleep(0.1)

#     ##### HELPER FUNCTIONS #############################################################

#     def update_connection(self):
#         """Updates connection state."""
#         self.connected = utilities.valid_internet_connection()
#         self.ip = utilities.get_ip()
#         self.wifis = utilities.get_wifis()
#         self.is_iot_registered = utilities.is_registered_with_iot()
#         self.device_id = utilities.get_device_id()
#         self.iot_connection = self.state.iot.get("connected")
