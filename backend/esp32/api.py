from fastapi import FastAPI, HTTPException
import requests
from typing import List, Dict
import asyncio
import socket

app = FastAPI()

# Przykładowa lista ESP - w rzeczywistości może być to dynamiczne
esp_devices = {
    "esp1": "192.168.0.101",
    "esp2": "192.168.0.102",
    "esp3": "192.168.0.103",
    "esp4": "192.168.0.104"
}

@app.get("/devices", response_model=Dict[str, str])
async def get_devices():
    # Zwraca listę dostępnych urządzeń ESP
    return esp_devices

@app.post("/send-data/{device_id}")
async def send_data(device_id: str, var1: int, var2: int):
    if device_id not in esp_devices:
        raise HTTPException(status_code=404, detail="Device not found")

    esp_ip = esp_devices[device_id]
    try:
        url = f"http://{esp_ip}/receive-data"
        response = requests.post(url, json={"var1": var1, "var2": var2})
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
