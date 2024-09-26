from fastapi import FastAPI
import uvicorn
from esp32_back import app1
from octa_back import app2

app = FastAPI()

# Dodajemy trasy z obu aplikacji
app.mount("/app1", app1)
app.mount("/app2", app2)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
