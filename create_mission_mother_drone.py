from pymavlink import mavutil

class MissionPlanner:
    def __init__(self, connection_string):
        """
        Inicjalizacja klasy MissionPlanner.
        """
        self.connection_string = connection_string
        self.vehicle = self.connect_to_vehicle()
        self.mission_items = []

    def connect_to_vehicle(self):
        """
        Funkcja do połączenia się z pojazdem.
        """
        vehicle = mavutil.mavlink_connection(self.connection_string)
        vehicle.wait_heartbeat()
        print("Połączono z pojazdem!")
        return vehicle

    def create_takeoff_command(self, altitude):
        """
        Funkcja do stworzenia komendy TAKEOFF.
        """
        return mavutil.mavlink.MAVLink_mission_item_message(
            0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 
            0, 0, 0, 0, 0, 0, altitude
        )

    def create_waypoint_command(self, lat, lon, altitude, delay=0):
        """
        Funkcja do stworzenia komendy WAYPOINT z opcjonalnym opóźnieniem.
        """
        return mavutil.mavlink.MAVLink_mission_item_message(
            0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 
            delay, 0, 0, 0, lat, lon, altitude
        )

    def create_do_set_servo_command(self, servo_number, pwm_value, duration=0):
        """
        Funkcja do stworzenia komendy DO_SET_SERVO z opcjonalnym czasem trwania.
        """
        return mavutil.mavlink.MAVLink_mission_item_message(
            0, 0, 0, mavutil.mavlink.MAV_FRAME_MISSION, 
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 1, 
            servo_number, pwm_value, 0, 0, 0, 0, 0, duration
        )

    def create_return_to_launch_command(self):
        """
        Funkcja do stworzenia komendy RETURN_TO_LAUNCH (RTL).
        """
        return mavutil.mavlink.MAVLink_mission_item_message(
            0, 0, 0, mavutil.mavlink.MAV_FRAME_MISSION, 
            mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 1, 
            0, 0, 0, 0, 0, 0, 0
        )

    def add_takeoff(self, altitude):
        """
        Dodaje komendę TAKEOFF do misji.
        """
        self.mission_items.append(self.create_takeoff_command(altitude))

    def add_waypoint(self, lat, lon, altitude, delay=0):
        """
        Dodaje komendę WAYPOINT do misji z opcjonalnym opóźnieniem.
        """
        self.mission_items.append(self.create_waypoint_command(lat, lon, altitude, delay))

    def add_do_set_servo(self, servo_number, pwm_value, duration=0):
        """
        Dodaje komendę DO_SET_SERVO do misji z opcjonalnym czasem trwania.
        """
        self.mission_items.append(self.create_do_set_servo_command(servo_number, pwm_value, duration))

    def add_return_to_launch(self):
        """
        Dodaje komendę RETURN_TO_LAUNCH do misji.
        """
        self.mission_items.append(self.create_return_to_launch_command())

    def upload_mission(self):
        """
        Funkcja do wgrania misji do pojazdu.
        """
        mission_count = len(self.mission_items)
        self.vehicle.mav.mission_count_send(self.vehicle.target_system, self.vehicle.target_component, mission_count)

        for i, item in enumerate(self.mission_items):
            self.vehicle.mav.send(item)
            print(f"Komenda {i + 1}/{mission_count} wysłana.")

        print("Misja wgrana pomyślnie!")

    def close_connection(self):
        """
        Zamknięcie połączenia z pojazdem.
        """
        self.vehicle.close()
        print("Połączenie zamknięte.")

if __name__ == "__main__":
    planner = MissionPlanner('udpin:localhost:14550')

    planner.add_takeoff(altitude=10)
    planner.add_waypoint(lat=47.397742, lon=8.545593, altitude=10, delay=5)  # 5 sekund opóźnienia
    planner.add_do_set_servo(servo_number=9, pwm_value=1500, duration=2)  # 2 sekundy trwania
    planner.add_waypoint(lat=47.397850, lon=8.545700, altitude=10, delay=3)  # 3 sekundy opóźnienia
    planner.add_return_to_launch()

    # Wgranie misji do pojazdu
    planner.upload_mission()

    # Zamknięcie połączenia
    planner.close_connection()
