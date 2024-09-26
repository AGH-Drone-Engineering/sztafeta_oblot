FROM python:3.10-slim

WORKDIR /app

# Copy the dependencies file to the working directory
COPY ./backend/mission_main ./
   
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003

# Command to run the application
CMD ["python","app.py"]
