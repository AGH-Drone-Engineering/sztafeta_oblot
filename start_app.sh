#!/bin/bash

# Uruchomienie aplikacji Streamlit
echo "Uruchamianie aplikacji Streamlit..."
streamlit run frontend/mission_upload.py &

# Uruchomienie aplikacji backend ESP32
echo "Uruchamianie backendu..."
python3 backend/all_backend/backend.py &

# Oczekiwanie na zakończenie wszystkich procesów
wait

echo "Wszystkie aplikacje zostały uruchomione."