from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import uvicorn
from createmission import MissionPlanner


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

app = FastAPI()

class DataFramePayload(BaseModel):
    data: str

@app.post("/upload")
async def upload(payload: DataFramePayload):
    data = payload.data
    if data:
        df = pd.read_json(data, orient='split')
        print(df)
        print(parse_dataframe(df))
        # print(df)
        # create_mission = MissionPlanner()
        
        
        
        return {"message": "Data received successfully"}

    else:
        return {"message": "No data received"}, 400

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
