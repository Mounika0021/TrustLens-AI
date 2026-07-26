# TrustLens AI

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![PyTorch](https://img.shields.io/badge/PyTorch-DeepLearning-red)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

An AI-powered Identity Document Verification System that combines **OCR**, **MRZ extraction**, **Computer Vision**, and **Vision-Language Models (Qwen2-VL + LoRA)** to automatically verify identity documents and generate explainable verification results.

TrustLens AI extracts information from identity documents, validates extracted fields, performs AI-based reasoning, computes a trust score, and exposes production-ready REST APIs using **FastAPI**.

---

# Table of Contents

- Overview
- Features
- System Architecture
- Technology Stack
- Project Structure
- API Endpoints
- Sample API Response
- Installation
- Running the Application
- Docker Deployment
- Model Pipeline
- Future Improvements
- Author

---

# Overview

Identity verification is an essential component of modern digital applications including:

- Banking
- Financial Services
- Digital KYC
- Online Account Opening
- Government Portals
- Travel Verification

TrustLens AI automates the verification process using Artificial Intelligence by combining OCR, document validation, and Vision-Language reasoning.

The system is designed to be modular, scalable, and deployment-ready.

---

# Features

✅ OCR-based text extraction using EasyOCR

✅ Passport MRZ extraction

✅ Identity field extraction

- Name
- Date of Birth
- Gender
- ID Number
- Nationality
- Expiry Date (Passport)

✅ Identity validation rules

✅ AI reasoning using Qwen2-VL

✅ LoRA fine-tuned Vision-Language Model

✅ Explainable AI responses

✅ Trust Score generation

✅ Fraud risk assessment

✅ FastAPI REST APIs

✅ Docker support

---

# System Architecture

```text
                 User Upload
                      │
                      ▼
          Image Preprocessing
             (OpenCV + PIL)
                      │
                      ▼
                OCR (EasyOCR)
                      │
                      ▼
            MRZ Extraction (Passport)
                      │
                      ▼
             Field Extraction Engine
                      │
                      ▼
           Identity Validation Rules
                      │
                      ▼
        Vision-Language Model (Qwen2-VL)
                      │
                      ▼
          LoRA Fine-Tuned Reasoning
                      │
                      ▼
            Trust Score Computation
                      │
                      ▼
          FastAPI REST API Response
```

---

# Technology Stack

| Component | Technology |
|------------|------------|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Deep Learning | PyTorch |
| OCR | EasyOCR |
| Image Processing | OpenCV, Pillow |
| Vision Language Model | Qwen2-VL |
| Fine-tuning | PEFT (LoRA) |
| Transformers | Hugging Face |
| API Documentation | Swagger UI |
| Deployment | Docker |

---

# Project Structure

```text
TrustLens-AI/

├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── inference.py
│   ├── mrz.py
│   ├── ocr.py
│   ├── reasoning.py
│   ├── schemas.py
│   ├── trust_score.py
│   ├── utils.py
│   └── validation.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore
```

---

# API Endpoints

## Verify Identity Document

```
POST /verify
```

Uploads an identity document and returns the verification result.

---

## Sample Response

```json
{
  "document_type": "Passport",
  "verification_status": "Verified",
  "trust_score": 0.96,
  "validation": {
    "name": true,
    "dob": true,
    "passport_number": true
  },
  "reasoning": "The extracted identity information is internally consistent. No suspicious inconsistencies were detected."
}
```

---

# API Documentation

Once the FastAPI server is running:

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/Mounika0021/TrustLens-AI.git
```

Move into the project directory

```bash
cd TrustLens-AI
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Application

Start the FastAPI server

```bash
uvicorn api.app:app --reload
```

Server

```
http://localhost:8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

---

# Docker Deployment

Build Docker Image

```bash
docker build -t trustlens-ai .
```

Run Docker Container

```bash
docker run -p 8000:8000 trustlens-ai
```

---

# Model Pipeline

1. Upload identity document
2. Image preprocessing
3. OCR using EasyOCR
4. MRZ extraction (Passport)
5. Field extraction
6. Identity validation
7. Vision-Language reasoning using Qwen2-VL
8. LoRA-enhanced inference
9. Trust score computation
10. Return explainable verification result

---

# Current Modules

| Module | Description |
|----------|-------------|
| OCR | Extracts text from uploaded documents |
| MRZ | Extracts passport MRZ information |
| Validation | Performs identity consistency checks |
| Inference | Runs Qwen2-VL model |
| Reasoning | Generates explainable AI responses |
| Trust Score | Computes document confidence score |
| FastAPI | Serves REST API endpoints |

---

# Future Improvements

- Selfie vs ID face matching
- Aadhaar QR code verification
- PAN card verification improvements
- Digital signature verification
- Multi-language OCR support
- Batch document verification
- Cloud deployment (AWS / Azure / GCP)
- CI/CD using GitHub Actions
- Kubernetes deployment

---

# Author

**Ravakutam Mounika**

Machine Learning Engineer | Computer Vision | Vision-Language Models | Generative AI

GitHub

https://github.com/Mounika0021

---

## License

This project is intended for educational, research, and demonstration purposes.
