
-- ==========================================================
-- Hospital Management System Schema
-- PostgreSQL / DrawSQL Import
-- ==========================================================

DROP TABLE IF EXISTS inventory_transactions CASCADE;
DROP TABLE IF EXISTS prescriptions CASCADE;
DROP TABLE IF EXISTS visits CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS medicines CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    employee_code VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    gender VARCHAR(10),
    dob DATE,
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash TEXT NOT NULL,
    department VARCHAR(100),
    specialization VARCHAR(100),
    license_number VARCHAR(60),
    joining_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    role_id BIGSERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_roles (
    user_role_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    assigned_by BIGINT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_user_role UNIQUE(user_id,role_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY(role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY(assigned_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE patients (
    patient_id BIGSERIAL PRIMARY KEY,
    patient_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    gender VARCHAR(10),
    dob DATE,
    blood_group VARCHAR(5),
    phone VARCHAR(15),
    email VARCHAR(100),
    address TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    allergies TEXT,
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medicines (
    medicine_id BIGSERIAL PRIMARY KEY,
    medicine_name VARCHAR(100) NOT NULL,
    generic_name VARCHAR(100),
    category VARCHAR(50),
    dosage_form VARCHAR(50),
    strength VARCHAR(50),
    manufacturer VARCHAR(100),
    unit_price NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    inventory_id BIGSERIAL PRIMARY KEY,
    medicine_id BIGINT NOT NULL,
    batch_number VARCHAR(50) NOT NULL,
    expiry_date DATE,
    purchase_price NUMERIC(10,2),
    selling_price NUMERIC(10,2),
    quantity_in_stock INT DEFAULT 0,
    minimum_stock INT DEFAULT 0,
    supplier VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(medicine_id) REFERENCES medicines(medicine_id)
);

CREATE TABLE visits (
    visit_id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    doctor_id BIGINT NOT NULL,
    visit_type VARCHAR(20) DEFAULT 'OUTPATIENT',
    visit_status VARCHAR(20) DEFAULT 'OPEN',
    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admission_date TIMESTAMP,
    discharge_date TIMESTAMP,
    chief_complaint TEXT,
    diagnosis TEXT,
    treatment_plan TEXT,
    notes TEXT,
    height NUMERIC(5,2),
    weight NUMERIC(5,2),
    temperature NUMERIC(4,1),
    blood_pressure VARCHAR(20),
    pulse_rate INT,
    oxygen_level INT,
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY(doctor_id) REFERENCES users(user_id)
);

CREATE TABLE prescriptions (
    prescription_id BIGSERIAL PRIMARY KEY,
    visit_id BIGINT NOT NULL,
    inventory_id BIGINT NOT NULL,
    prescribed_by BIGINT NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    duration VARCHAR(50),
    quantity INT,
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(visit_id) REFERENCES visits(visit_id) ON DELETE CASCADE,
    FOREIGN KEY(inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY(prescribed_by) REFERENCES users(user_id)
);

CREATE TABLE inventory_transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    inventory_id BIGINT NOT NULL,
    transaction_type VARCHAR(20),
    quantity INT NOT NULL,
    reference_type VARCHAR(30),
    reference_id BIGINT,
    performed_by BIGINT,
    remarks TEXT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(inventory_id) REFERENCES inventory(inventory_id) ON DELETE CASCADE,
    FOREIGN KEY(performed_by) REFERENCES users(user_id)
);

CREATE INDEX idx_visit_patient ON visits(patient_id);
CREATE INDEX idx_visit_doctor ON visits(doctor_id);
CREATE INDEX idx_prescription_visit ON prescriptions(visit_id);
CREATE INDEX idx_inventory_medicine ON inventory(medicine_id);
CREATE INDEX idx_inventory_txn ON inventory_transactions(inventory_id);

/* ==========================================================
   LAB TEST CATALOG
   Master table for all laboratory tests
   ========================================================== */

CREATE TABLE lab_test_catalog (
    test_id BIGSERIAL PRIMARY KEY,
    test_code VARCHAR(20) UNIQUE NOT NULL,
    test_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    sample_type VARCHAR(50),
    unit VARCHAR(30),
    reference_range VARCHAR(100),
    normal_min NUMERIC(10,2),
    normal_max NUMERIC(10,2),
    default_price NUMERIC(10,2),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



/* ==========================================================
   LABORATORY
   Stores laboratory requests
   ========================================================== */

CREATE TABLE laboratory (

    lab_id BIGSERIAL PRIMARY KEY,

    visit_id BIGINT NOT NULL,

    patient_id BIGINT NOT NULL,

    requested_by BIGINT NOT NULL,

    lab_technician_id BIGINT,

    priority VARCHAR(20) DEFAULT 'NORMAL',

    sample_type VARCHAR(50),

    sample_collected_at TIMESTAMP,

    test_status VARCHAR(30) DEFAULT 'PENDING',

    remarks TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    FOREIGN KEY (visit_id)
        REFERENCES visits(visit_id)
        ON DELETE CASCADE,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    FOREIGN KEY (requested_by)
        REFERENCES users(user_id),

    FOREIGN KEY (lab_technician_id)
        REFERENCES users(user_id)
);



/* ==========================================================
   LAB REPORT
   Multiple test results can belong to one laboratory request
   ========================================================== */

CREATE TABLE lab_report (

    lab_report_id BIGSERIAL PRIMARY KEY,

    lab_id BIGINT NOT NULL,

    test_id BIGINT NOT NULL,

    patient_id BIGINT NOT NULL,

    doctor_id BIGINT NOT NULL,

    report_number VARCHAR(30) UNIQUE NOT NULL,

    result TEXT NOT NULL,

    unit VARCHAR(30),

    reference_range VARCHAR(100),

    is_abnormal BOOLEAN DEFAULT FALSE,

    remarks TEXT,

    verified_by BIGINT,

    verified_at TIMESTAMP,

    report_file TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lab_id)
        REFERENCES laboratory(lab_id)
        ON DELETE CASCADE,

    FOREIGN KEY (test_id)
        REFERENCES lab_test_catalog(test_id),

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    FOREIGN KEY (doctor_id)
        REFERENCES users(user_id),

    FOREIGN KEY (verified_by)
        REFERENCES users(user_id)
);



/* ==========================================================
   DOCTOR REPORT
   Doctor consultation report
   ========================================================== */

CREATE TABLE doctor_report (

    doctor_report_id BIGSERIAL PRIMARY KEY,

    visit_id BIGINT NOT NULL,

    patient_id BIGINT NOT NULL,

    doctor_id BIGINT NOT NULL,

    report_number VARCHAR(30) UNIQUE NOT NULL,

    chief_complaint TEXT,

    clinical_findings TEXT,

    diagnosis TEXT,

    treatment_plan TEXT,

    prescribed_medicines TEXT,

    doctor_notes TEXT,

    follow_up_required BOOLEAN DEFAULT FALSE,

    follow_up_date DATE,

    next_visit_reason TEXT,

    report_file TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (visit_id)
        REFERENCES visits(visit_id)
        ON DELETE CASCADE,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    FOREIGN KEY (doctor_id)
        REFERENCES users(user_id)
);



/* ==========================================================
   INDEXES
   ========================================================== */

CREATE INDEX idx_lab_visit
ON laboratory(visit_id);

CREATE INDEX idx_lab_patient
ON laboratory(patient_id);

CREATE INDEX idx_lab_status
ON laboratory(test_status);

CREATE INDEX idx_lab_requested_by
ON laboratory(requested_by);

CREATE INDEX idx_lab_report_lab
ON lab_report(lab_id);

CREATE INDEX idx_lab_report_test
ON lab_report(test_id);

CREATE INDEX idx_lab_report_patient
ON lab_report(patient_id);

CREATE INDEX idx_lab_report_doctor
ON lab_report(doctor_id);

CREATE INDEX idx_doctor_report_visit
ON doctor_report(visit_id);

CREATE INDEX idx_doctor_report_patient
ON doctor_report(patient_id);

CREATE INDEX idx_doctor_report_doctor
ON doctor_report(doctor_id);

INSERT INTO roles(role_name,description) VALUES
('Administrator','System Administrator'),
('Doctor','Medical Practitioner'),
('Nurse','Nursing Staff'),
('Receptionist','Reception'),
('Pharmacist','Pharmacy'),
('Lab Technician','Laboratory'),
('Inventory Manager','Inventory'),
('Accountant','Billing'),
('Patient','Portal User');
