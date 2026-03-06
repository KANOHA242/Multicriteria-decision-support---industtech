# Multicriteria-decision-support---industtech
# 🏭 Multicriteria Decision Dashboard — Industtech Maroc

> **Course project** — Multicriteria Decision Analysis (ADM)  
> **Author** — KANOHA ELENGA Jihane  
> **Method** — AHP (Analytic Hierarchy Process) + Linear Optimization

---

## 📌 Overview

This project builds an **interactive multicriteria decision support system** to evaluate, prioritize, and optimally select digital transformation projects for a fictional Moroccan industrial company, **Industtech Maroc**, operating in the manufacturing of mechanical parts for the automotive and agro-industrial sectors.

The core question addressed:

> *How can a company identify and select the most relevant digital transformation projects, balancing technical feasibility, economic return, and environmental impact — under budget constraints?*

---

## 🏗️ Project Structure

```
industtech-adm/
│
├── dashboard.py                # Streamlit interactive dashboard
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── Notebook/
│   └── ahp_calculs.ipynb       # Step-by-step AHP computations (Jupyter)
│
├── data/
│   └── donnees_projets.csv     # Projects, costs, AHP scores
│
└── rapport/
    └── rapport_final.docx      # Final written report
```

---

## 🎯 Candidate Projects

| ID | Project | Description | Budget (kMAD) |
|----|---------|-------------|---------------|
| P1 | **AutoProd** | Production line automation (robots, conveyors) | 850 |
| P2 | **IoT-Predict** | IoT sensors for predictive maintenance | 420 |
| P3 | **DataPerf** | Performance analytics dashboard (ERP/MES) | 280 |
| P4 | **GreenEnergy** | Energy efficiency solutions (solar + heat recovery) | 560 |
| P5 | **DigitalTwin** | Digital twin of a manufacturing line | 690 |

**Total available budget: 1 500 kMAD**

---

## ⚖️ Evaluation Criteria (AHP)

| ID | Criterion | Weight |
|----|-----------|--------|
| C1 | Economic impact (ROI, productivity gains) | 20.6% |
| C2 | Technical feasibility (maturity, skills) | 11.8% |
| C3 | Sustainability / Environmental impact | 20.6% |
| C4 | Strategic alignment with Industry 4.0 vision | **43.0%** |
| C5 | Implementation complexity (risk, delays) | 4.0% |

Weights derived from pairwise comparison matrices using **Saaty's scale** (Consistency Ratio CR = 0.062 ✅).

---

## 🔢 Methodology

### Step 1 — AHP (Analytic Hierarchy Process)
1. Define evaluation criteria and candidate projects
2. Build pairwise comparison matrices (Saaty's 1–9 scale)
3. Compute criteria weights via eigenvector normalization
4. Verify consistency (CR < 0.10)
5. Compute local scores per criterion and global AHP scores

### Step 2 — Linear Optimization
- **Objective**: maximize total AHP score of selected projects
- **Constraint**: total cost ≤ available budget
- **Method**: exhaustive combinatorial search (5 projects → 31 combinations)
- **Tool**: native Python (`itertools`) — no external solver required

### Optimal solution (budget = 1 500 kMAD)

| Selected | Score | Cost |
|----------|-------|------|
| ✅ P2 IoT-Predict + P3 DataPerf + P4 GreenEnergy | **0.5386** | 1 260 kMAD |

---

## 📊 Dashboard Features

The Streamlit dashboard includes 4 pages:

| Page | Content |
|------|---------|
| 🏠 Overview | KPIs, project table, criteria weights, global ranking |
| ⚖️ AHP Analysis | Radar chart, heatmap, per-criterion breakdown |
| 💰 Budget Optimization | Interactive budget slider, optimal selection, score vs. budget curve |
| 🔬 Scenarios | Custom criteria weights, live ranking changes, sensitivity analysis |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git https://github.com/KANOHA242/Multicriteria-decision-support---industtech.git

```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the dashboard
```bash
streamlit run dashboard.py       or
python -m streamlit run "dashboard.py"
```

The app will open automatically at `http://localhost:8501`

---

## 📚 References

- **Saaty, T.L.** (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
- **Culaste et al.** (2022). *A Decision Support System for the Optimal Allocation of Limited Resources in the COVID-19 Pandemic*. ISAHP 2022.
- **Palma, Bianco & Salomon** (2024). *Bibliometric Study on AHP and Investment Decisions in Industry 4.0*. ISAHP 2024.
- **Frank et al.** (2019). Industry 4.0 technologies: implementation patterns in manufacturing companies.

---

## 📄 License

This project is academic and was developed as part of the Multicriteria Decision Analysis (ADM) course. Feel free to use or adapt it for educational purposes with proper attribution.