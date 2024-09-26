# Use the latest Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the files and install dependencies
COPY ./frontend ./
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8501 for Streamlit
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "mission_upload.py", "--server.port=8501", "--server.address=0.0.0.0"]
