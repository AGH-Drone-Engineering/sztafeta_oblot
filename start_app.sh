#!/bin/bash

# Uruchomienie aplikacji Streamlit
echo "Uruchamianie aplikacji Streamlit..."
streamlit run frontend/mission_upload.py &

# # Uruchomienie aplikacji backend ESP32
# echo "Uruchamianie aplikacji ESP32..."
# python3 backend/esp32/app/main.py &

# # Uruchomienie głównej aplikacji misji
# echo "Uruchamianie głównej aplikacji misji..."
# python3 backend/mission_main/app.py &

python3 backend/all_backend/backend.py &
# Oczekiwanie na zakończenie wszystkich procesów
wait

echo "Wszystkie aplikacje zostały uruchomione."
