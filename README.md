<p align="center">
  <h1 align="center"> Atrium AI – AI-Driven Building Planning Assistant</h1>
  <p align="center">
    Kesava Prasad Arul · Georgy Chomakhashvili · Gustavo Gurgel · Martin Steinmayer · Thomas Wölkhart 
  </p>
</p>

<div align="center">

</div>

---

## 🧱 What is Atrium AI?

**Atrium AI** is an end-to-end AI platform that automates the _early-phase technical planning_ of buildings.  
It reads Excel-based _technical room books_, _room type lists_, _cost data_, and _planning documents_ — and turns them into structured outputs such as:

- 🧩 **Automated room classification**
- 🔥 **Performance estimation (heating, cooling, ventilation, etc.)**
- 💰 **Cost estimation per trade (DIN 276)**
- 📄 **Pre-filled explanatory reports (DOCX/PDF)**

Instead of manually maintaining dozens of Excel sheets, engineers can now use one unified pipeline powered by **structured data processing** and **large language models (LLMs)**.

<div align="center">
  <img src="assets/system_overview.png" alt="Atrium AI Overview" width="90%">
  <br>
  <em>Atrium AI automates classification, power estimation, cost prediction, and report generation.</em>
</div>

---

## 💡 Why It Matters

- ⏱️ **Saves weeks** of manual room type classification
- 📊 **Improves estimation accuracy** by learning from historical projects
- 🧠 **Understands Excel, PDF, and Word data** using context-aware LLMs
- 🧾 **Standardized outputs** aligned with DIN 276 and technical room book conventions
- 🏗️ **Scalable** across trades (heating, cooling, ventilation, electrical, etc.)

---

## ⚙️ Core Modules

### 🏷️ 1. Room Type Classification

Assigns a **standardized room type** (e.g., “001 Office”, “WC”, “Server Room”) to each room in the technical room book using LLM-based fuzzy matching and a curated synonym/mapping catalog.

**Input:**

- Room book Excel (Room name, use, area, volume, etc.)
- Standard room type list

**Output:**

- Excel with assigned room type and confidence score

---

### 🔥 2. Power Requirement Estimation

Calculates **heating, cooling, ventilation, and electrical loads** using known reference values from room type tables combined with room-specific parameters.

**Input:**

- Room type assignments
- Room metrics (area, volume, window area, etc.)
- Old project performance data

**Output:**

- Estimated power requirement table (W/m²) per trade

---

### 💰 3. Cost Estimation

Predicts **trade-level and total building costs** using data from:

- BKI characteristic values (€/m², €/kW)
- Historic project data
- Current performance values and parameters

**Output:**

- Cost breakdown per trade (DIN 276 KG 400)
- Total project cost (Excel/CSV)

---

### 🧾 4. Explanatory Report Generator

Creates a **structured, pre-filled project report** summarizing assumptions, standards, system sizes, and cost breakdown — tailored to project type and federal state regulations.

**Output formats:**

- DOCX / Markdown / PDF

---

## 🧰 Quickstart

<!-- 1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Run the end-to-end pipeline**

```bash
python main.py
```

3. **Generate the explanatory report**

```bash
python generate_report.py --input outputs/performance_and_costs.xlsx --template templates/report.docx
``` -->

✅ Automatically handles Excel/PDF parsing  
✅ Uses LLMs for contextual reasoning (OpenAI GPT / Gemini)  
✅ Produces ready-to-submit planning deliverables

---

## 🧠 Tech Stack

| Layer               | Tools & Frameworks                          |
| ------------------- | ------------------------------------------- |
| **Data Parsing**    | Pandas, openpyxl, pdfplumber                |
| **AI Reasoning**    | Gemini                                      |
| **Matching Engine** | Full-Text-Search, custom synonym dictionary |
| **Backend**         | Python 3.11, FastAPI                        |
| **Frontend**        | Next.js Dashboard                           |
| **Outputs**         | Excel, DOCX, PDF                            |

---

## ❤️ Acknowledgements

Developed during the **BKW Hackathon 2025** with data from **technical room books, BKI standards, and real project archives**.  
Special thanks to mentors and partners from **BKW**, **TUM.ai**, and **industry experts** who provided feedback and domain insight.
