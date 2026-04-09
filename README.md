# 🏗️ TradeFlow.ai — AI-Powered Renovation Project Planner

> Transform simple home project descriptions into structured, real-world execution plans using AI.

---

## 📌 Overview

**TradeFlow.ai** is an intelligent project planning system that leverages LLMs (Groq + LLaMA) to generate complete renovation plans from natural language input.

Users describe their project in plain English, and the system produces:

- 📅 Detailed timelines (days & weeks)  
- 💰 Budget estimates (CAD)  
- 👷 Required trades & responsibilities  
- 🧩 Task dependencies & sequencing  
- ⚖️ Real-world trade-offs  
- ⚠️ Risks with mitigation strategies  
- 📋 Phase-by-phase execution roadmap  

Unlike traditional tools, this system uses AI reasoning, not templates or rule-based logic.

---

## ✨ Key Features

### 🧠 AI-Driven Planning
- Powered by Groq LLaMA models  
- Fully dynamic — no predefined workflows  
- Context-aware decision making  

### 📊 Structured Project Breakdown
- Multi-phase construction planning  
- Task-level dependency mapping  
- Contractor assignment per task  

### 📈 Visual Intelligence
- Interactive dependency graph (Plotly + NetworkX)  
- Timeline visualization  
- Trade effort distribution  

### ⚖️ Decision Support System
- Practical trade-offs (DIY vs professional, materials, etc.)  
- Risk analysis with actionable mitigation  

### 📤 Export Capabilities
- CSV (project schedule)  
- Text report (print-ready documentation)  

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| AI Engine | Groq API (LLaMA, Mixtral, Gemma) |
| Visualization | Plotly, NetworkX |
| Data Processing | Pandas, JSON |

---

## 📂 Project Structure

TradeFlow.ai/

├── app.py

├── requirements.txt

└── README.md

---

## ⚙️ Installation & Setup

1. Clone repository
   git clone https://github.com/your-username/tradeflow-ai.git
   cd tradeflow-ai

2. Install dependencies
   pip install -r requirements.txt

3. Run application
   python -m streamlit run tradeflow_app.py

---

## 🔑 API Configuration

- Get your free API key from: https://console.groq.com  
- Paste it in the app sidebar

---

## 🚀 How It Works

1. User enters project description  
2. AI processes input via Groq  
3. Returns structured JSON plan  
4. App visualizes plan  

---

## 🧪 Example Input

I want to renovate my kitchen with new cabinets, countertops, and lighting.
Budget is around $15,000 and timeline is 4 weeks.

---

## 🎯 Use Cases

- Homeowners planning renovations  
- Contractors creating structured plans  
- Academic AI project  
- Project management learning  

---

## ⚠️ Disclaimer

AI-generated estimates. Always verify with professionals.

---

## 📚 Academic Context

MAI 104 — AI in Project Management

---

## 🔮 Future Improvements

- Multi-project comparison  
- Mobile UI  
- Chat-based assistant  
- PDF export  
- Location-based pricing  

