FROM python:3.10-slim

WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .
   
RUN pip install --no-cache-dir -r requirements.txt

VOLUME [ "/app" ]

EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "mother_mission:app", "--host", "0.0.0.0", "--port", "8001"]