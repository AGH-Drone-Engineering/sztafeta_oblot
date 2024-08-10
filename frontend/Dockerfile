# Używamy oficjalnego obrazu Python jako bazowego
FROM python:3.9-slim

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Skopiowanie pliku requirements.txt do kontenera
COPY requirements.txt .

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "mission_upload.py", "--server.port=8501", "--server.address=0.0.0.0"]
