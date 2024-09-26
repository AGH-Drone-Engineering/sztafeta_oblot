from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from createmission import MissionPlanner

app2 = FastAPI()  # Zmieniono nazwę instancji na app2, aby uniknąć konfliktu nazw

def parse_row(row):
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        if row['drop'] == 0:
            return {"add_waypoint": [row['latitude'], row['longitude']], "delay": row['delay']}
        elif row['drop'] == 1 and pd.notna(row['servo']):
            if pd.notna(row['drop_delay']):
                return {"add_waypoint": [row['latitude'], row['longitude']], "delay": row['delay'], 
                        "set_servo": row['servo'], "drop_delay": row['drop_delay']}
    elif pd.isna(row['latitude']) and pd.isna(row['longitude']) and pd.notna(row['delay']):
        return {"delay": row['delay']}
    return None

def parse_dataframe(df):
    results = []
    for _, row in df.iterrows():
        result = parse_row(row)
        if result:
            results.append(result)
    return results

class DataFramePayload(BaseModel):
    data: str
    ip: str
    port: int
    height: int

@app2.post("/upload")
async def upload(payload: DataFramePayload):
    data = payload.data
    if data:
        pd.options.display.float_format = '{:.8f}'.format
        df = pd.read_json(data, orient='split')
        
        ip, port = payload.ip, payload.port
        height = payload.height
        parsed_data = parse_dataframe(df)
        try:
            planner = MissionPlanner(f'udpin:{ip}:{port}')
        except Exception as e:
            return {"message": "Cannot communicate with vehicle" + str(e)}, 400
        
        try:
            planner.add_takeoff(altitude=height)
            
            for command in parsed_data:
                if ('add_waypoint' in command and 'delay' in command 
                      and 'set_servo' in command and 'drop_delay' in command):
                    planner.add_waypoint(lat=command['add_waypoint'][0], lon=command['add_waypoint'][1], 
                                         altitude=height, delay=command['delay'])
                    planner.set_servo(servo_number=command['set_servo'], pwm=1500)
                    planner.set_delay(delay_seconds=command['drop_delay'])
                elif 'add_waypoint' in command and 'delay' in command:
                    planner.add_waypoint(lat=command['add_waypoint'][0], lon=command['add_waypoint'][1], 
                                         altitude=height, delay=command['delay'])
                elif 'delay' in command:
                    planner.set_delay(delay_seconds=command['delay'])
                else:
                    return {"message": f"Invalid data received {command} "}, 400
            planner.add_return_to_launch()
            
            mission_upload_status = planner.upload_mission()
            planner.close_connection()
            if mission_upload_status == True:
                return {"message": "Data received successfully"}
            else:
                return {"message": "Mission upload failed"}, 400
        except Exception as e:
            return {"message": str(e)}, 400
    else:
        return {"message": "No data received"}, 400
