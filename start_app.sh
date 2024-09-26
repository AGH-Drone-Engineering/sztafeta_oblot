#!/bin/bash

# Funkcja, która zostanie uruchomiona, gdy skrypt otrzyma sygnał zakończenia
cleanup() {
    echo "Zamykanie aplikacji..."
    # Zabijanie wszystkich uruchomionych w tle procesów
    pkill -P $$
    echo "Wszystkie procesy zostały zakończone."
    exit 0
}

# Ustawienie pułapki na sygnały SIGINT (Ctrl+C) oraz SIGTERM
trap cleanup SIGINT SIGTERM

# Uruchomienie aplikacji Streamlit
echo "Uruchamianie aplikacji Streamlit..."
streamlit run frontend/mission_upload.py &

# Uruchomienie aplikacji backend ESP32
echo "Uruchamianie backendu..."
python3 backend/all_backend/backend.py &

# Oczekiwanie na zakończenie wszystkich procesów
wait
