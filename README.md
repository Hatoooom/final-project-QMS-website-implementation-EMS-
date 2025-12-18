# 🚑 EMS Command & Control System (ISO-CMD)

![Status](https://img.shields.io/badge/Status-Complete-success)
![Standard](https://img.shields.io/badge/ISO-22320%20Compliant-blue)
![Python](https://img.shields.io/badge/Built%20With-Flask-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

> A full-stack Emergency Management System simulation designed to enforce **ISO 22320** operational standards, featuring automated safety protocols and real-time asset tracking.


---

## 🔭 Project Overview

The **EMS ISO-CMD** system is a web-based simulation of an Emergency Operations Center (EOC). Unlike simple tracking apps, this system implements a strict **Quality Management System (QMS)**. It focuses on the critical balance between operational speed and asset safety.

The system integrates:
* **Command & Control (C2):** Real-time visualization of assets.
* **Logistics:** Tracking of critical medical supplies.
* **Auditability:** Immutable logging of incident timestamps.

---

## ✨ Key Features

* **🗺️ Command Map:** A geospatial dashboard showing "Single Source of Truth" for all units.
* **🚑 Fleet Readiness Logic:** Monitors Fuel, Health, and Supply levels dynamically.
* **⏱️ Precision Logging:** Records $T_0$ (Call), $T_1$ (Dispatch), $T_2$ (Arrival), and $T_3$ (Return).
* **🛡️ Automated QMS Gate:** prevents the dispatch of unsafe vehicles (e.g., low fuel or damaged hull), ensuring adherence to **ISO 22320** safety protocols.

---

## 🛠 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python (Flask) | REST API & Game Logic |
| **Database** | PostgreSQL (Neon) | Persistent State & Logs |
| **Frontend** | HTML5 / JS | Interactive Dashboard |
| **Analytics** | Chart.js | Real-time performance graphing |

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/ems-iso-cmd.git](https://github.com/your-username/ems-iso-cmd.git)
cd ems-iso-cmd
``` 

### 2.Install Dependencies
```bash
pip install requirements.txt
```

### 3. Configure Database
```bash
DATABASE_URL = "postgres://user:pass@ep-cool-project.aws.neon.tech/neondb?sslmode=require"
```

### 4. Run the Application
```bash
python app.py
```
