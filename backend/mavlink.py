from pymavlink import mavutil, mavwp
import time

# Parametry połączenia
connection_string = 'localhost:14550'

# Połączenie z dronem
mav = mavutil.mavlink_connection('udpin:127.0.0.1:14550')
mav.wait_heartbeat()
print("HEARTBEAT OK\n")

# Tworzenie Waypointów
wp = mavwp.MAVWPLoader()

waypoints = [
    (37.5090904347, 127.045094298),
    (37.509070898, 127.048905867),
    (37.5063678607, 127.048960654),
    (37.5061713129, 127.044741936),
    (37.5078823794, 127.046914506)
]

home_location = waypoints[0]

# Dodawanie waypointów do misji
for seq, (lat, lon) in enumerate(waypoints):
    frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
    altitude = 15  # Wysokość 15 metrów
    autocontinue = 1
    current = 0
    param1 = 15.0  # minimal pitch

    if seq == 0:  # Pierwszy waypoint - takeoff
        current = 1
        p = mavutil.mavlink.MAVLink_mission_item_message(mav.target_system, mav.target_component, seq, frame, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, current, autocontinue, param1, 0, 0, 0, lat, lon, altitude)
    elif seq == len(waypoints) - 1:  # Ostatni waypoint - land
        p = mavutil.mavlink.MAVLink_mission_item_message(mav.target_system, mav.target_component, seq, frame, mavutil.mavlink.MAV_CMD_NAV_LAND, current, autocontinue, 0, 0, 0, 0, lat, lon, altitude)
    else:  # Waypoint
        p = mavutil.mavlink.MAVLink_mission_item_message(mav.target_system, mav.target_component, seq, frame, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, current, autocontinue, 0, 0, 0, 0, lat, lon, altitude)
    
    wp.add(p)

# Funkcja ustawienia lokalizacji domu
def cmd_set_home(home_location, altitude):
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_HOME,
        1,  # ustawienie pozycji
        0, 0, 0, 0, 
        home_location[0],  # lat
        home_location[1],  # lon
        altitude  # alt
    )

# Funkcja pobrania lokalizacji domu
def cmd_get_home():
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_GET_HOME_POSITION,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    msg = mav.recv_match(type=['COMMAND_ACK'], blocking=True)
    print(msg)
    msg = mav.recv_match(type=['HOME_POSITION'], blocking=True)
    return (msg.latitude, msg.longitude, msg.altitude)

# Ustawienie lokalizacji domu
cmd_set_home(home_location, 0)
msg = mav.recv_match(type=['COMMAND_ACK'], blocking=True)
print(msg)
print(f'Set home location: {home_location[0]} {home_location[1]}')
time.sleep(1)

# Pobranie lokalizacji domu
home_location = cmd_get_home()
print(f'Get home location: {home_location[0]} {home_location[1]} {home_location[2]}')
time.sleep(1)

# Wysyłanie waypointów do drona
mav.waypoint_clear_all_send()
mav.waypoint_count_send(wp.count())

for i in range(wp.count()):
    msg = mav.recv_match(type=['MISSION_REQUEST'], blocking=True)
    mav.mav.send(wp.wp(msg.seq))
    print(f'Sending waypoint {msg.seq}')       

msg = mav.recv_match(type=['MISSION_ACK'], blocking=True)  # OKAY
print(msg.type)

# Odczytywanie waypointów z drona
mav.waypoint_request_list_send()
msg = mav.recv_match(type=['MISSION_COUNT'], blocking=True)
waypoint_count = msg.count
print(msg.count)

for i in range(waypoint_count):
    mav.waypoint_request_send(i)
    msg = mav.recv_match(type=['MISSION_ITEM'], blocking=True)
    print(f'Receiving waypoint {msg.seq}')       
    print(msg)

mav.mav.mission_ack_send(mav.target_system, mav.target_component, 0)  # OKAY

# Zmiana trybu misji
PX4_MAV_MODE = 209.0
PX4_CUSTOM_MAIN_MODE_AUTO = 4.0
PX4_CUSTOM_SUB_MODE_AUTO_MISSION = 4.0

mav.mav.command_long_send(
    1, 1, mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
    PX4_MAV_MODE,
    PX4_CUSTOM_MAIN_MODE_AUTO, PX4_CUSTOM_SUB_MODE_AUTO_MISSION, 0, 0, 0, 0
)

msg = mav.recv_match(type=['COMMAND_ACK'], blocking=True)
print(msg)

# Wysyłanie Heartbeat
mav.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 192, 0, 4)

# ARMowanie drona
mav.mav.command_long_send(
    1, 1, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
    1,
    0, 0, 0, 0, 0, 0
)
msg = mav.recv_match(type=['COMMAND_ACK'], blocking=True)
print(msg)

# Monitorowanie postępu misji
nextwaypoint = 0
relative_alt = 0

def handle_mission_current(msg, nextwaypoint):
    if msg.seq > nextwaypoint:
        print(f"Moving to waypoint {msg.seq}")
        nextwaypoint = msg.seq + 1
        print(f"Next Waypoint {nextwaypoint}")
    return nextwaypoint

def handle_global_position_int(msg):
    pass  # Można tu dodać więcej logiki, jeśli potrzebne

while True:
    try:
        msg = mav.recv_match(type=['GLOBAL_POSITION_INT', 'MISSION_CURRENT', 'HEARTBEAT'], blocking=True, timeout=0.5)
        if not msg:
            continue
        if msg.get_type() == 'HEARTBEAT':
            mav.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 192, 0, 4)
        elif msg.get_type() == 'GLOBAL_POSITION_INT':
            handle_global_position_int(msg)
            relative_alt = msg.relative_alt
        elif msg.get_type() == 'MISSION_CURRENT':
            nextwaypoint = handle_mission_current(msg, nextwaypoint)
            if nextwaypoint >= waypoint_count - 1 and relative_alt <= 1 * 1000 * 0.05: 
                print("Reached land altitude")
                break
        time.sleep(0.1)
        mav.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 192, 0, 4)
    except KeyboardInterrupt:
        break

# DISARMowanie drona
mav.mav.command_long_send(
    1, 1, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
    0,
    0, 0, 0, 0, 0, 0
)
msg = mav.recv_match(type=['COMMAND_ACK'], blocking=True)
print(msg)

time.sleep(1)
