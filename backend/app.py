from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import uvicorn

app = FastAPI()

class DataFramePayload(BaseModel):
    data: str

@app.post("/upload")
async def upload(payload: DataFramePayload):
    data = payload.data
    if data:
        df = pd.read_json(data, orient='split')
        print("Received DataFrame:")
        print(df)
        return {"message": "Data received successfully"}
    else:
        return {"message": "No data received"}, 400

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
