# HyperVerify AI

An end-to-end AI-powered identity verification system that combines OCR, Computer Vision, and Vision-Language Models (VLMs) to verify identity documents such as Aadhaar, PAN, and Passports.

The system extracts document information, validates identity fields, detects suspicious patterns, explains verification decisions using a Vision-Language Model, and exposes production-ready REST APIs using FastAPI.

---

## Features

- OCR-based text extraction
- Automatic document type detection
- Field extraction (Name, DOB, ID Number, Gender, Address)
- Identity consistency validation
- Vision-Language reasoning using Qwen2-VL
- Fraud risk scoring
- Explainable AI responses
- LoRA fine-tuning using PEFT
- FastAPI REST APIs
- Dockerized deployment
- Gradio web interface

---

## System Architecture

```
               User Upload
                    │
                    ▼
          Document Preprocessing
          (OpenCV + Image Enhancement)
                    │
                    ▼
             OCR (EasyOCR)
                    │
                    ▼
          Field Extraction Engine
                    │
                    ▼
      Identity Validation Rules
                    │
                    ▼
        Vision-Language Model
             (Qwen2-VL)
                    │
                    ▼
       LoRA Fine-tuned Model
                    │
                    ▼
       Fraud Risk Assessment
                    │
                    ▼
     FastAPI REST API Response
                    │
                    ▼
         Gradio Web Interface
```

---

## Tech Stack

| Component | Technology |
|------------|------------|
| Language | Python |
| Deep Learning | PyTorch |
| OCR | EasyOCR |
| Vision | OpenCV |
| Transformers | Hugging Face |
| Vision Language Model | Qwen2-VL |
| Fine-tuning | PEFT (LoRA) |
| Backend | FastAPI |
| Frontend | Gradio |
| Deployment | Docker |

---

## Project Structure

```
HyperVerify-AI/

├── app/
│   ├── api.py
│   ├── ocr.py
│   ├── validator.py
│   ├── vlm.py
│   ├── explain.py
│   └── utils.py
│
├── models/
│
├── data/
│
├── notebooks/
│
├── screenshots/
│
├── Dockerfile
├── requirements.txt
├── README.md
└── app.py
```

---

## API Endpoints

### Verify Document

```
POST /verify
```

Uploads an identity document and returns verification status.

Example Response

```json
{
  "document":"Aadhaar",
  "status":"Verified",
  "risk_score":0.08,
  "fields":{
      "name":"John Doe",
      "dob":"01-01-2000",
      "id_number":"XXXX XXXX 1234"
  },
  "explanation":"No suspicious inconsistencies detected."
}
```

---

### OCR

```
POST /ocr
```

Extracts all readable text from the uploaded document.

---

### Explain

```
POST /explain
```

Returns a natural language explanation of suspicious regions detected by the Vision-Language Model.

---

### Health

```
GET /health
```

Checks API status.

---

## Model Pipeline

1. Upload document
2. Image preprocessing
3. OCR using EasyOCR
4. Field extraction
5. Validation rules
6. Vision-Language reasoning
7. LoRA fine-tuned verification
8. Risk scoring
9. API response

---

## Evaluation Metrics

The system is evaluated using:

- Accuracy
- Precision
- Recall
- F1-score

The fine-tuned model is compared against the base Vision-Language Model to measure performance improvements.

---

## Docker

Build

```bash
docker build -t hyperverify .
```

Run

```bash
docker run -p 8000:8000 hyperverify
```

---

## Run Locally

Install dependencies

```bash
pip install -r requirements.txt
```

Start API

```bash
uvicorn app:app --reload
```

Open

```
http://localhost:8000/docs
```

---

## Future Improvements

- Face matching between selfie and ID
- QR code validation for Aadhaar
- Digital signature verification
- Multi-language OCR
- Cloud deployment (AWS/GCP)
- CI/CD pipeline using GitHub Actions

---

## Author

**Ravakutam Mounika**

Machine Learning | Computer Vision | Vision-Language Models
