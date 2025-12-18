# Project Report: EMS Command & Control System (ISO-CMD)

**Project Title:** ISO-Compliant Emergency Management System Simulation  
**Date:** December 18, 2025  
**Subject:** Technical Report on System Architecture, QMS Implementation, and Operational Challenges  

---

## 1. Executive Summary

The **EMS Command & Control (ISO-CMD)** system is a web-based simulation designed to replicate the operational environment of an Emergency Operations Center (EOC). The project aims to demonstrate how software can enforce **ISO 22320:2011** standards (Societal Security – Emergency Management).

The system integrates real-time asset tracking, inventory logistics, and incident logging into a single "Single Source of Truth" dashboard. A key focus of the project was the implementation of a Quality Management System (QMS) to prevent operational failures, specifically addressing the conflict between rapid response demands and asset safety maintenance.

---

## 2. Project Objectives

The primary goal was to build a full-stack application that does not just "work," but adheres to specific engineering and safety standards.

* **Objective A:** Visualize the "Common Operational Picture" (COP) required by incident commanders.
* **Objective B:** Implement strict resource management logic (Fuel, Health, Medical Supplies).
* **Objective C:** Create an immutable audit log of all emergency events ($T_0$ to $T_3$ timestamps).
* **Objective D:** Identify and resolve a critical operational failure using algorithmic logic gates.

---

## 3. System Architecture

The project utilizes a modern web stack designed for reliability and speed:

### 3.1 Backend Infrastructure
* **Framework:** Python Flask.
* **Database:** PostgreSQL (hosted on Neon Tech).
* **Role:** The API acts as the central authority. It receives requests for incident creation, dispatch, and maintenance, ensuring that the database state remains consistent.

### 3.2 Database Schema
The data model consists of three core entities:
1.  **`ambulances`:** Stores dynamic state (Fuel %, Health %, Location, Status).
2.  **`inventory`:** Tracks consumable hospital supplies (Bandages, Oxygen Tanks).
3.  **`incidents`:** An append-only log of emergency calls with precise timestamps for audit purposes.

### 3.3 Frontend Interface
* **Dashboard:** A "Command Map" providing geospatial visualization of assets.
* **Fleet Status:** A dedicated panel for monitoring vehicle telemetry.
* **Logistics:** An inventory management screen for restocking supplies.

---

## 4. Quality Management System (QMS) & ISO Standards

The project was strictly guided by **ISO 22320**, which dictates requirements for incident response.

### 4.1 Standard: Command and Control
* **ISO Requirement:** Effective coordination requires a shared operational picture.
* **Implementation:** The "Command Map" view allows the user to see exactly where every unit is (Idle, Dispatched, On Scene) in real-time. This eliminates information asymmetry.

### 4.2 Standard: Operational Information
* **ISO Requirement:** Information must be accurate, timely, and reliable.
* **Implementation:** We implemented a 4-point timestamp logging system.
    * **$T_0$ (Call Received):** The moment the incident is generated.
    * **$T_1$ (Dispatch):** The moment a unit is assigned.
    * **$T_2$ (Arrival):** The moment the unit reaches the scene.
    * **$T_3$ (Closure):** The moment the unit returns and the file is closed.

---

## 5. Critical Challenge & Resolution (Detailed Narrative)

A significant engineering challenge was encountered during the "Stress Test" phase of development. This section details the problem, the root cause, and the technical resolution.

### 5.1 The Problem: "The Zombie Unit" Scenario
During continuous simulation runs, we observed a flaw in the operational logic. When emergency calls were frequent, the operator (user) would instinctively dispatch the nearest available unit repeatedly.

* **Observation:** Ambulance `AMB-01` was dispatched 5 times in a row.
* **The Failure:** The system allowed `AMB-01` to respond to the 6th call even though its **Fuel was at 0%** and its **Health was at 10%** (Catastrophic Damage).
* **Impact:** In a real-world scenario, this would result in a vehicle breakdown en route to a dying patient, a total failure of the ISO requirement for "Operational Readiness."

### 5.2 The Conflict
We faced a trade-off between **Availability** (dispatching anyone to save time) and **Safety** (grounding vehicles for maintenance). The initial code prioritized availability, leading to unsafe operations.

### 5.3 The Resolution: Algorithmic Gatekeeping
To fix this, we implemented a strict **"Compliance Gate"** within the dispatch algorithm. We treated the Dispatch button not as a simple switch, but as a conditional request.

**The Logic Implemented:**
We defined a set of "Inviolable Standards":
1.  **Fuel Minimum:** 30%
2.  **Health Minimum:** 50%
3.  **Supplies:** Must be stocked.

**The Code Solution (Concept):**
We wrote a function `checkCompliance()` that runs *before* any dispatch is authorized.

```javascript
function checkCompliance(vehicle) {
    if (vehicle.fuel < 30) return "REJECTED: Fuel Critical";
    if (vehicle.health < 50) return "REJECTED: Hull Breach";
    return "APPROVED";
}
