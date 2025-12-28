# 🪑 FurnitureFlip — AI-Assisted Furniture Resale Analytics Platform

FurnitureFlip is a full-stack analytics application that helps users evaluate the resale potential of used furniture.  
It combines conversational input, dynamic form generation, online price comparisons, and visual analytics — all deployed using Docker and Kubernetes.

---

## 🚀 Key Features

- 💬 **Chat-Driven Item Detection**
  - Users describe what they want to sell (e.g., *“I want to sell a chair”*)
  - The system automatically detects the furniture category

- 🧾 **Dynamic Form Generation**
  - Context-aware form fields based on item type
  - Validated inputs for pricing, condition, material, and repair costs

- 🌐 **Online Price Comparisons**
  - Fetches real-world comparable listings (“comps”)
  - Extracts and normalizes price signals

- 📊 **Analytics Dashboard**
  - Price distribution visualizations
  - Scatter plots for market variability
  - Estimated resale price & profitability insights

- 🧠 **Backend Validation & Business Logic**
  - Server-side validation using FastAPI + Pydantic
  - Robust handling of edge cases and malformed inputs

---

## 🧱 Architecture
```
┌────────────┐ HTTP ┌──────────────┐
│ Streamlit │ ─────────────▶ │ FastAPI API │
│ Frontend │ │ Backend │
└────────────┘ └──────────────┘
│ │
│ ▼
│ Pricing Logic
│ Comps Fetching
│
▼
Kubernetes (Docker Desktop)
```

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit**
- Python
- Interactive charts & forms

### Backend
- **FastAPI**
- Pydantic (data validation)
- Custom pricing & comparison logic

### DevOps / Infrastructure
- Docker
- Kubernetes (k8s)
- NodePort services
- Health checks & readiness probes

---

## 📁 Project Structure
```
FurnitureFlip-k8s/
│
├── backend/
│ ├── main.py # FastAPI application
│ ├── comps.py # Online comps logic
│ ├── pricing.py # Pricing & profit calculations
│ ├── Dockerfile
│ └── requirements.txt
│
├── frontend/
│ ├── app.py # Streamlit UI
│ ├── Dockerfile
│ └── requirements.txt
│
├── k8s/
│ ├── backend.yaml
│ ├── frontend.yaml
│ └── google-secret.yaml
│
├── .gitignore
└── README.md
```

---

## ▶️ Running the App (Local with Kubernetes)

### 1️⃣ Build Docker Images
```bash
docker build -t furnitureflip-backend:1.0 backend/
docker build -t furnitureflip-frontend:1.0 frontend/
```
### 2️⃣ Deploy to Kubernetes
```bash
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```
### 3️⃣ Access the App
```bash
http://localhost:30851
```

📌 Example Workflow

User types: 

1. “I want to sell a chair”

2. System detects category → generates form

3. User submits pricing & condition

4. Backend validates & processes data

5. Dashboard shows market price insights


🎯 Why This Project Matters

- FurnitureFlip demonstrates:

- End-to-end full-stack engineering

- Real-world data validation challenges

- Microservices deployment using Kubernetes

- Analytics-driven decision support

-This project was built with production-grade practices and is suitable for real-world resale platforms.

Author

Madhukar Goli
MS in Business Analytics
Aspiring Business / Data Analyst

🔗 GitHub: https://github.com/madhukargoli1992G

🔗 LinkedIn: https://www.linkedin.com/in/madhukargoli/
🔗 LinkedIn: https://www.linkedin.com/in/madhukargoli/
