# Hospital Management System

A comprehensive, robust, and extensible Hospital Management System built with Python, Flask, and PostgreSQL. This application is powered by an EAV (Entity-Attribute-Value) CRUD engine, providing flexible and dynamic data models without requiring hardcoded schema migrations for every change.

## 🚀 Features

The application provides specialized modules to handle various aspects of hospital operations:

### 👥 User & Role Management
- **Role-Based Access Control (RBAC):** Distinct roles including Admin, Doctor, Nurse, Pharmacist, Lab Technician, and Receptionist.
- Secure authentication and session management using `Flask-Login`.

### 🏥 Patient Management
- Complete patient demographics tracking (Name, Gender, DOB, Blood Group, Contact Info).
- Medical history and allergy logging.

### 🩺 Visits & Clinical Care
- **Visit Tracking:** Record Outpatient (OPD) and Inpatient (IPD) visits.
- **Vital Signs:** Track vitals such as blood pressure, pulse rate, oxygen level, height, weight, and temperature per visit.
- **Doctor Reports:** Detailed clinical findings, diagnosis, treatment plans, and follow-up schedules.

### 💊 Pharmacy & Inventory
- **Medicine Catalog:** Centralized catalog of medicines with generic names, categories, and unit prices.
- **Inventory Management:** Track batch numbers, expiry dates, purchase/selling prices, and quantity in stock.
- **Inventory Transactions:** Log all stock movements (incoming/outgoing/adjustments).
- **Prescriptions:** Link prescribed medicines to specific patient visits.

### 🔬 Laboratory
- **Lab Test Catalog:** Standardized catalog of lab tests with reference ranges, sample types, and normal limits.
- **Lab Requests & Reports:** Track lab requests by priority, sample collection status, and detailed result entry with automatic abnormality detection.

## 🛠️ Technology Stack

- **Backend Framework:** Flask 3.1
- **Database:** PostgreSQL (using `psycopg2`)
- **ORM & Data Layer:** SQLAlchemy 2.0 with dynamic EAV CRUD engine (`hogc.engines.crud`)
- **Authentication:** Flask-Login, Werkzeug for hashing
- **Forms & Validation:** WTForms, email-validator
- **Templating:** Jinja2

## ⚙️ Installation & Setup

Follow these steps to set up the project locally:

### 1. Prerequisites
- Python 3.10+
- PostgreSQL server
- Git

### 2. Clone the Repository
```bash
git clone <repository_url>
cd <repository_name>
```

### 3. Create a Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Variables
Create a `.env` file in the root directory with the following configurations:
```env
# Example .env configuration
FLASK_DEBUG=1
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=your_secure_secret_key
DATABASE_URL=postgresql://username:password@localhost:5432/hospital_db
LOG_LEVEL=INFO
```
*(Adjust the `DATABASE_URL` with your actual PostgreSQL credentials.)*

### 6. Database Initialization
Ensure your PostgreSQL database is created. The application uses a dynamic EAV pattern. When you run the application for the first time, it will automatically create the necessary base tables and seed the dynamic modules, fields, and relationships via `app.crud_init.initialize_crud_metadata()`.

### 7. Run the Application
```bash
python run.py
```
The server will start at `http://localhost:5000` (or as configured in `.env`).

## 📖 How to Use

1. **Login:** Access the web interface and log in with your assigned credentials.
2. **Dashboard:** Depending on your role (e.g., Doctor, Admin), you will be redirected to the relevant dashboard.
3. **Patients & Visits:** Receptionists/Nurses can register patients and create new visits.
4. **Clinical Examination:** Doctors can select a visit, add vital signs, record clinical findings, and generate prescriptions or lab requests.
5. **Pharmacy:** Pharmacists can view prescriptions, dispense medicines (which updates the inventory), and manage medicine stocks.
6. **Laboratory:** Lab Technicians can view requested tests, enter results, and generate final lab reports for doctors to review.

## 🏗️ Architecture Note
This system leverages a custom EAV (Entity-Attribute-Value) schema module under the `hogc` library. Instead of traditional static SQLAlchemy models for every entity (like Patient, Medicine, etc.), entities are defined dynamically as `Modules` with configured `Fields` and `Relationships`. This makes the system highly adaptable to new requirements.
