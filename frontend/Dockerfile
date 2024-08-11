FROM python:3.9-slim

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj pliki wymagań do katalogu roboczego
COPY requirements.txt ./ 

# Zainstaluj zależności
RUN pip install --no-cache-dir -r requirements.txt


# Ustaw zmienną środowiskową, aby Streamlit nie próbował otworzyć przeglądarki
ENV STREAMLIT_SERVER_PORT=8501

# Informuj Docker, że kontener będzie nasłuchiwał na określonym porcie podczas działania
EXPOSE 8501

VOLUME [ "/app" ]

CMD ["streamlit", "run", "mission_upload.py", "--server.port=8501", "--server.address=0.0.0.0"]
