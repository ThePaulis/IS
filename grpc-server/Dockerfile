#Base image
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

#Expose the gRPC port
EXPOSE 50051
#Start the gRPC server
CMD ["python", "main.py"]