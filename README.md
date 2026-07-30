# PSX Mentor - FYP Prototype

This repository contains the prototype implementation for the **PSX Mentor** system, demonstrating an intelligent, 5-module architecture for technical and fundamental analysis of the Pakistan Stock Exchange.

## 📁 File Structure

The project files are logically structured to map to the 5 modules of the system:

```text
Prototype PSX/
│
├── Data Engine (Module 1)
│   ├── fetch_data.py          # Connects to Yahoo Finance API to pull live market data
│   ├── psx_data.json          # Live data output used by the frontend dashboard
│   └── requirements.txt       # Python dependencies for the data engine
│
├── Frontend Application (Modules 2 - 5)
│   ├── psx_mentor_prototype_landing.html  # Entry point. The architectural overview.
│   ├── index.html                         # Module 5: Portfolio Management Dashboard
│   ├── stock_details.html                 # Module 3: Fundamental Trust Layer (Details)
│   └── ENGRO_dashboard_v2 (2).html        # Modules 2 & 4: Deep dive AI report (Technical & GenAI)
│
├── Assets
│   ├── styles.css             # Premium CSS styling (glassmorphism, dark mode)
│   └── app.js                 # Dashboard logic, charting, and PDF generation
│
└── Docs
    └── fyp.docx               # Academic project documentation
```

## ⚙️ Requirements to Run

### 1. Python Environment (For Live Data)
To run **Module 1 (Data Engine)** and fetch live PSX data, you need Python installed on your system.
Install the required libraries by running:
```bash
pip install -r requirements.txt
```

### 2. Local Web Server (For the Dashboard)
Modern web browsers block JavaScript from reading local JSON files for security reasons (CORS policy). To view the dashboard properly, you must serve the files via a local server.

**To run the entire project:**
1. Fetch the latest live data:
   ```bash
   python fetch_data.py
   ```
2. Start the local server:
   ```bash
   python -m http.server 8000
   ```
3. Open your browser and navigate to:
   [http://localhost:8000/psx_mentor_prototype_landing.html](http://localhost:8000/psx_mentor_prototype_landing.html)
