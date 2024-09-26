#!/bin/bash

# Zapytanie użytkownika o uruchomienie mavproxy
read -p "Czy chcesz uruchomić mavproxy? (y/n): " uruchom_proxy

if [[ "$uruchom_proxy" == "y" || "$uruchom_proxy" == "Y" ]]; then
    echo "Uruchamianie mavproxy..."
    mavproxy.py --master=/dev/ttyACM0 --out=udp:127.0.0.1:14550 --out=udp:127.0.0.1:14551 &
    MAVPROXY_PID=$!
    if [ $? -ne 0 ]; then
      echo "Błąd: Nie udało się uruchomić mavproxy."
      exit 1
    fi
else
    echo "Pominięto uruchamianie mavproxy."
fi

# Uruchamianie aplikacji Streamlit
echo "Uruchamianie aplikacji Streamlit..."
streamlit run frontend/mission_upload.py &
STREAMLIT_PID=$!
if [ $? -ne 0 ]; then
  echo "Błąd: Nie udało się uruchomić aplikacji Streamlit."
  exit 1
fi

# Uruchamianie backendu ESP32 (odkomentuj, jeśli potrzebne)
# echo "Uruchamianie aplikacji ESP32..."
# python3 backend/esp32/app/main.py &
# ESP32_PID=$!
# if [ $? -ne 0 ]; then
#   echo "Błąd: Nie udało się uruchomić aplikacji ESP32."
#   exit 1
# fi

# Uruchamianie głównej aplikacji misji (odkomentuj, jeśli potrzebne)
# echo "Uruchamianie głównej aplikacji misji..."
# python3 backend/mission_main/app.py &
# MISSION_PID=$!
# if [ $? -ne 0 ]; then
#   echo "Błąd: Nie udało się uruchomić głównej aplikacji misji."
#   exit 1
# fi

# Uruchamianie głównego backendu
echo "Uruchamianie głównego backendu..."
python3 backend/all_backend/backend.py &
BACKEND_PID=$!
if [ $? -ne 0 ]; then
  echo "Błąd: Nie udało się uruchomić głównego backendu."
  exit 1
fi

# Oczekiwanie na zakończenie wszystkich procesów
wait $STREAMLIT_PID $BACKEND_PID

if [[ "$uruchom_proxy" == "y" || "$uruchom_proxy" == "Y" ]]; then
    wait $MAVPROXY_PID
fi

echo "Wszystkie aplikacje zostały uruchomione."
