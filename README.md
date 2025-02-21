# Paystubs-Assessment

## Project Overview
Paystubs-Assessment is a Python-based application designed to process payroll data and generate paystubs. This project includes a set of scripts and functionalities to handle payroll calculations, generate PDF paystubs, and send them via email.

## Features
- Process payroll data from CSV files
- Generate PDF paystubs
- Send paystubs via email
- Dockerized for easy deployment

## Getting Started
### Prerequisites
- Python 3.x
- Docker

### Installation
1. Clone the repository:
```bash
git clone https://github.com/huanhaowu/Paystubs-Assessment.git
cd Paystubs-Assessment
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Run  the application
```bash
python app.py
```

## Docker Integration
This project includes a Dockerfile for containerization. The Docker image is uploaded to Docker Hub, allowing for easy deployment and scalability.


## Using Docker

To build and run the Docker container:

### Build the Docker image

```bash
docker build -t paystubs-assessment .
```

### Run the Docker image
```bash
docker run -d -p 5000:5000 paystubs-assessment
```

## Docker Hub

The Docker image for this project is available on Docker Hub. You can pull the image using the following command:
```bash
docker pull your-dockerhub-username/paystubs-assessment
```
