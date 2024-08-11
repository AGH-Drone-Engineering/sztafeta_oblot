from pymavlink import mavutil, mavwp

class DroneMission:
    def __init__(self, connection_string='localhost:14550'):
        self.connection_string = connection_string
        self.mav = mavutil.mavlink_connection('udpin:127.0.0.1:14550')
        self.mav.wait_heartbeat()
        print("HEARTBEAT OK\n")
        self.wp_loader = mavwp.MAVWPLoader()
        self.home_position = self.get_current_position()

    def get_current_position(self):
        print("Getting current position...")
        msg = self.mav.recv_match(type=['GLOBAL_POSITION_INT'], blocking=True)
        latitude = msg.lat * 1e-7
        longitude = msg.lon * 1e-7
        altitude = msg.relative_alt * 1e-3  # altitude in meters
        print(f"Current position: lat={latitude}, lon={longitude}, alt={altitude}")
        return latitude, longitude, altitude

    def add_waypoint(self, latitude, longitude, altitude=15):
        seq = len(self.wp_loader.wpoints)
        frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        autocontinue = 1
        current = 0

        waypoint = mavutil.mavlink.MAVLink_mission_item_message(
            self.mav.target_system, self.mav.target_component, seq, frame, 
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, current, autocontinue, 
            0, 0, 0, 0, latitude, longitude, altitude)

        self.wp_loader.add(waypoint)

    def upload_mission(self):
        # Add takeoff point at the current position
        takeoff_lat, takeoff_lon, takeoff_alt = self.home_position
        self.add_takeoff(takeoff_lat, takeoff_lon, takeoff_alt + 10)  # add 10 meters to current altitude for takeoff

        # Add landing point at the current position
        self.add_landing(takeoff_lat, takeoff_lon)

        self.mav.waypoint_clear_all_send()
        self.mav.waypoint_count_send(self.wp_loader.count())

        for i in range(self.wp_loader.count()):
            msg = self.mav.recv_match(type=['MISSION_REQUEST'], blocking=True)
            self.mav.mav.send(self.wp_loader.wp(msg.seq))
            print(f'Sending waypoint {msg.seq}')       

        msg = self.mav.recv_match(type=['MISSION_ACK'], blocking=True)  # OKAY
        print(msg.type)

    def add_takeoff(self, latitude, longitude, altitude):
        seq = len(self.wp_loader.wpoints)
        frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        autocontinue = 1
        current = 1
        param1 = 15.0  # minimal pitch for takeoff

        waypoint = mavutil.mavlink.MAVLink_mission_item_message(
            self.mav.target_system, self.mav.target_component, seq, frame, 
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, current, autocontinue, 
            param1, 0, 0, 0, latitude, longitude, altitude)

        self.wp_loader.add(waypoint)

    def add_landing(self, latitude, longitude):
        seq = len(self.wp_loader.wpoints)
        frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        autocontinue = 1
        current = 0

        waypoint = mavutil.mavlink.MAVLink_mission_item_message(
            self.mav.target_system, self.mav.target_component, seq, frame, 
            mavutil.mavlink.MAV_CMD_NAV_LAND, current, autocontinue, 
            0, 0, 0, 0, latitude, longitude, 0)

        self.wp_loader.add(waypoint)

    def start_mission(self):
        PX4_MAV_MODE = 209.0
        PX4_CUSTOM_MAIN_MODE_AUTO = 4.0
        PX4_CUSTOM_SUB_MODE_AUTO_MISSION = 4.0

        self.mav.mav.command_long_send(
            1, 1, mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            PX4_MAV_MODE,
            PX4_CUSTOM_MAIN_MODE_AUTO, PX4_CUSTOM_SUB_MODE_AUTO_MISSION, 0, 0, 0, 0
        )

        msg = self.mav.recv_match(type=['COMMAND_ACK'], blocking=True)
        print(msg)
        print("Mission started")

# Przykład użycia
mission = DroneMission()

# Dodaj punkty do misji (poza punktem startu i lądowania)

# mission.add_waypoint(37.509070898, 127.048905867)
# mission.add_waypoint(37.5063678607, 127.048960654)
# mission.add_waypoint(37.5061713129, 127.044741936)

# Prześlij misję do drona
mission.upload_mission()

# Rozpocznij misję
# mission.start_mission()
