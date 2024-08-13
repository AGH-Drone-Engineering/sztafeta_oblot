from pymavlink import mavutil, mavwp

class MissionPlanner:
    def __init__(self, connection_string):
        """
        Inicjalizacja klasy MissionPlanner.
        """
        self.connection_string = connection_string
        # self.vehicle = self.connect_to_vehicle()
        self.mission_items = mavwp.MAVWPLoader()
        self.vehicle = mavutil.mavlink_connection(self.connection_string)
        self.vehicle.wait_heartbeat()
        # self.wp = 
    
    def create_takeoff_command(self, altitude):
        """
        Funkcja do stworzenia komendy TAKEOFF.
        """
        return mavutil.mavlink.MAVLink_mission_item_int_message(
            0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 
            0, 0, 0, 0, int(0 * 1e7), int(0 * 1e7), altitude
        )

    def create_waypoint_command(self, lat, lon, altitude, delay=0):
        """
        Funkcja do stworzenia komendy WAYPOINT z opcjonalnym opóźnieniem.
        """
        return mavutil.mavlink.MAVLink_mission_item_int_message(
            0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 
            delay, 0, 0, 0, int(lat * 1e7), int(lon * 1e7), altitude
        )

    def create_do_set_servo_command(self, servo_number, pwm_value, duration=0):
        """
        Funkcja do stworzenia komendy DO_SET_SERVO z opcjonalnym czasem trwania.
        """
        return mavutil.mavlink.MAVLink_mission_item_int_message(
            0, 0, 0, mavutil.mavlink.MAV_FRAME_MISSION, 
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 1, 
            servo_number, pwm_value, 0, 0, 0, 0, 0, duration
        )

    def create_return_to_launch_command(self):
        """
        Funkcja do stworzenia komendy RETURN_TO_LAUNCH (RTL).
        """
        return mavutil.mavlink.MAVLink_mission_item_int_message(
            0, 0, 0, mavutil.mavlink.MAV_FRAME_MISSION, 
            mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 1, 
            0, 0, 0, 0, 0, 0, 0
        )

    def add_takeoff(self, altitude):
        """
        Dodaje komendę TAKEOFF do misji.
        """
        self.mission_items.add(self.create_takeoff_command(altitude))

    def add_waypoint(self, lat, lon, altitude, delay=0):
        """
        Dodaje komendę WAYPOINT do misji z opcjonalnym opóźnieniem.
        """
        self.mission_items.add(self.create_waypoint_command(lat, lon, altitude, delay))

    def add_do_set_servo(self, servo_number, pwm_value, duration=0):
        """
        Dodaje komendę DO_SET_SERVO do misji z opcjonalnym czasem trwania.
        """
        self.mission_items.add(self.create_do_set_servo_command(servo_number, pwm_value, duration))

    def add_return_to_launch(self):
        """
        Dodaje komendę RETURN_TO_LAUNCH do misji.
        """
        self.mission_items.add(self.create_return_to_launch_command())

    
    
    def read_current_mission(self):
        self.vehicle.waypoint_request_list_send()
        waypoint_count = 0

        msg = self.vehicle.recv_match(type=['MISSION_COUNT'], blocking=True)
        waypoint_count = msg.count
        print(waypoint_count)

        for i in range(waypoint_count):
            self.vehicle.waypoint_request_send(i)
            msg = self.vehicle.recv_match(type=['MISSION_ITEM'], blocking=True)
            print(f'Receiving waypoint {msg.seq} ----------')
            print(msg)
            print('\n')

        self.vehicle.mav.mission_ack_send(self.vehicle.target_system, self.vehicle.target_component, 0)  
    
    def upload_mission(self):
        """
        Funkcja do wgrania misji do pojazdu.
        """
        self.vehicle.waypoint_clear_all_send()
        
        self.vehicle.waypoint_count_send(self.mission_items.count())

        for i in range(self.mission_items.count()):
            msg = self.vehicle.recv_match(type=['MISSION_REQUEST'], blocking=True)
            self.vehicle.mav.send(self.mission_items.wp(msg.seq))
            print(self.mission_items.wp(msg.seq))
            
        msg = self.vehicle.recv_match(type=['MISSION_ACK'], blocking=True)  # OKAY
        print(msg.type)
        print("Misja wgrana pomyślnie!")

    def arm_and_start_mission(self):
        """
        Uzbrojenie drona i rozpoczęcie misji.
        """
        self.vehicle.arducopter_arm()
        print("Dron uzbrojony.")
        
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_MISSION_START,
            0,
            0, 0, 0, 0, 0, 0, 0
        )
        print("Misja rozpoczęta!")

    def close_connection(self):
        """
        Zamknięcie połączenia z pojazdem.
        """
        self.vehicle.close()
        print("Połączenie zamknięte.")
        
    def set_servo(self, servo_number, pwm):
        #183 to jest komenda do ustwienia serwa 
        servo_message = mavutil.mavlink.MAVLink_mission_item_int_message(0, 0, 0,
                                                                         0, 183, 0, 
                                                                         1, float(servo_number), float(pwm), 
                                                                         0.0, 0.0, 0, 0, 0)
        self.mission_items.add(servo_message)

    def set_delay(self, delay_seconds: int):
        delay = mavutil.mavlink.MAVLink_mission_item_int_message(0, 0, 0,
                                                                0, 93, 0, 
                                                                1, float(delay_seconds), 0, 
                                                                0.0, 0.0, 0, 0, 0)
        
        self.mission_items.add(delay)



if __name__ == "__main__":
    
# MISSION_ITEM {target_system : 255, target_component : 0, seq : 2, frame : 0, command : 183, current : 0, autocontinue : 1, param1 : 1.0, param2 : 1500.0, param3 : 0.0, param4 : 0.0, x : 0.0, y : 0.0, z : 0.0, mission_type : 0}

    planner = MissionPlanner('udpin:localhost:14550')
    planner.read_current_mission()
    
    # Dodawanie nowej misji
    # planner.add_takeoff(altitude=10)
    # planner.add_waypoint(lat=47.397742, lon=8.545593, altitude=10, delay=5)  # 5 sekund opóźnienia
    # planner.set_servo(servo_number=1, pwm=1500)
    # planner.set_delay(delay_seconds=33)
    # planner.add_return_to_launch()

    # planner.upload_mission()
    