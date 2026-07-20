from app.extensions import db
from hogc.engines.crud.schema.module import Module
from hogc.engines.crud.schema.field import Field
from hogc.engines.crud.schema.relationship import RelationshipDefinition

def initialize_crud_metadata() -> None:
    """Seed modules, fields, and relationships in the CRUD engine database."""
    tenant_id = "default"
    org_id = "default"
    user_id = "system"

    # 1. Define Modules
    modules_data = {
        "user": ("User", "Users", "Application users and doctors"),
        "role": ("Role", "Roles", "User authorization roles"),
        "patient": ("Patient", "Patients", "Patient details and demographics"),
        "visit": ("Visit", "Visits", "Patient hospital visits"),
        "medicine": ("Medicine", "Medicines", "Catalog of available medicines"),
        "inventory": ("Inventory", "Inventory", "Stock levels of medicines"),
        "inventory_transaction": ("Inventory Transaction", "Inventory Transactions", "Inventory stock transaction logs"),
        "prescription": ("Prescription", "Prescriptions", "Medicines prescribed in visits"),
        "laboratory": ("Laboratory", "Laboratory requests", "Lab tests requested during visits"),
        "lab_test_catalog": ("Lab Test Catalog", "Lab Test Catalogs", "Catalog of laboratory tests"),
        "lab_report": ("Lab Report", "Lab Reports", "Laboratory test reports and results"),
        "report": ("Report", "Reports", "Doctor clinical reports and summaries"),
    }

    # 2. Define Fields for each module
    fields_data = {
        "user": [
            ("first_name", "First Name", "text", True, None),
            ("last_name", "Last Name", "text", False, None),
            ("email", "Email", "text", True, None),
            ("password_hash", "Password Hash", "text", True, None),
            ("status", "Status", "text", True, None),
            ("role", "Role", "text", False, None),
            ("employee_code", "Employee Code", "text", True, None),
            ("gender", "Gender", "text", False, None),
            ("dob", "Date of Birth", "text", False, None),
            ("phone", "Phone", "text", False, None),
            ("department", "Department", "text", False, None),
            ("specialization", "Specialization", "text", False, None),
            ("license_number", "License Number", "text", False, None),
            ("joining_date", "Joining Date", "text", False, None),
        ],
        "role": [
            ("name", "Name", "text", True, None),
            ("description", "Description", "text", False, None),
        ],
        "patient": [
            ("patient_number", "Patient Number", "text", True, None),
            ("first_name", "First Name", "text", True, None),
            ("last_name", "Last Name", "text", False, None),
            ("gender", "Gender", "text", False, None),
            ("dob", "Date of Birth", "text", False, None),
            ("blood_group", "Blood Group", "text", False, None),
            ("phone", "Phone", "text", False, None),
            ("email", "Email", "text", False, None),
            ("address", "Address", "text", False, None),
            ("emergency_contact_name", "Emergency Contact Name", "text", False, None),
            ("emergency_contact_phone", "Emergency Contact Phone", "text", False, None),
            ("allergies", "Allergies", "text", False, None),
            ("medical_history", "Medical History", "text", False, None),
        ],
        "visit": [
            ("visit_number", "Visit Number", "text", True, None),
            ("patient_id", "Patient ID", "text", True, None),
            ("doctor_id", "Doctor ID", "text", True, None),
            ("visit_type", "Visit Type", "text", True, None),
            ("visit_status", "Visit Status", "text", True, None),
            ("visit_date", "Visit Date", "text", True, None),
            ("admission_date", "Admission Date", "text", False, None),
            ("discharge_date", "Discharge Date", "text", False, None),
            ("chief_complaint", "Chief Complaint", "text", False, None),
            ("diagnosis", "Diagnosis", "text", False, None),
            ("treatment_plan", "Treatment Plan", "text", False, None),
            ("notes", "Notes", "text", False, None),
            ("height", "Height", "text", False, None),
            ("weight", "Weight", "text", False, None),
            ("temperature", "Temperature", "text", False, None),
            ("blood_pressure", "Blood Pressure", "text", False, None),
            ("pulse_rate", "Pulse Rate", "text", False, None),
            ("oxygen_level", "Oxygen Level", "text", False, None),
        ],
        "medicine": [
            ("medicine_name", "Medicine Name", "text", True, None),
            ("generic_name", "Generic Name", "text", False, None),
            ("category", "Category", "text", False, None),
            ("dosage_form", "Dosage Form", "text", False, None),
            ("strength", "Strength", "text", False, None),
            ("manufacturer", "Manufacturer", "text", False, None),
            ("unit_price", "Unit Price", "text", True, None),
        ],
        "inventory": [
            ("medicine_id", "Medicine ID", "text", True, None),
            ("batch_number", "Batch Number", "text", True, None),
            ("expiry_date", "Expiry Date", "text", False, None),
            ("purchase_price", "Purchase Price", "text", False, None),
            ("selling_price", "Selling Price", "text", False, None),
            ("quantity_in_stock", "Quantity in Stock", "text", True, None),
            ("minimum_stock", "Minimum Stock", "text", True, None),
            ("supplier", "Supplier", "text", False, None),
            ("last_updated", "Last Updated", "text", True, None),
        ],
        "inventory_transaction": [
            ("inventory_id", "Inventory ID", "text", True, None),
            ("performed_by", "Performed By", "text", False, None),
            ("transaction_type", "Transaction Type", "text", True, None),
            ("quantity", "Quantity", "text", True, None),
            ("reference_type", "Reference Type", "text", False, None),
            ("reference_id", "Reference ID", "text", False, None),
            ("remarks", "Remarks", "text", False, None),
            ("transaction_date", "Transaction Date", "text", True, None),
        ],
        "prescription": [
            ("visit_id", "Visit ID", "text", True, None),
            ("inventory_id", "Inventory ID", "text", True, None),
            ("dosage", "Dosage", "text", False, None),
            ("frequency", "Frequency", "text", False, None),
            ("duration", "Duration", "text", False, None),
            ("quantity", "Quantity", "text", False, None),
            ("instructions", "Instructions", "text", False, None),
            ("prescribed_by", "Prescribed By", "text", False, None),
        ],
        "laboratory": [
            ("visit_id", "Visit ID", "text", True, None),
            ("patient_id", "Patient ID", "text", True, None),
            ("requested_by", "Requested By", "text", True, None),
            ("lab_technician_id", "Lab Technician ID", "text", False, None),
            ("priority", "Priority", "text", True, None),
            ("sample_type", "Sample Type", "text", False, None),
            ("sample_collected_at", "Sample Collected At", "text", False, None),
            ("test_status", "Test Status", "text", True, None),
            ("remarks", "Remarks", "text", False, None),
            ("completed_at", "Completed At", "text", False, None),
        ],
        "lab_test_catalog": [
            ("test_code", "Test Code", "text", True, None),
            ("test_name", "Test Name", "text", True, None),
            ("category", "Category", "text", False, None),
            ("sample_type", "Sample Type", "text", False, None),
            ("unit", "Unit", "text", False, None),
            ("reference_range", "Reference Range", "text", False, None),
            ("normal_min", "Normal Min", "text", False, None),
            ("normal_max", "Normal Max", "text", False, None),
            ("default_price", "Default Price", "text", False, None),
            ("description", "Description", "text", False, None),
            ("is_active", "Is Active", "text", True, None),
        ],
        "lab_report": [
            ("lab_id", "Lab ID", "text", True, None),
            ("test_id", "Test ID", "text", True, None),
            ("patient_id", "Patient ID", "text", True, None),
            ("doctor_id", "Doctor ID", "text", True, None),
            ("verified_by", "Verified By", "text", False, None),
            ("report_number", "Report Number", "text", True, None),
            ("result", "Result", "text", True, None),
            ("unit", "Unit", "text", False, None),
            ("reference_range", "Reference Range", "text", False, None),
            ("is_abnormal", "Is Abnormal", "text", True, None),
            ("remarks", "Remarks", "text", False, None),
            ("verified_at", "Verified At", "text", False, None),
            ("report_file", "Report File", "text", False, None),
        ],
        "report": [
            ("visit_id", "Visit ID", "text", True, None),
            ("patient_id", "Patient ID", "text", True, None),
            ("doctor_id", "Doctor ID", "text", True, None),
            ("report_number", "Report Number", "text", True, None),
            ("chief_complaint", "Chief Complaint", "text", False, None),
            ("clinical_findings", "Clinical Findings", "text", False, None),
            ("diagnosis", "Diagnosis", "text", False, None),
            ("treatment_plan", "Treatment Plan", "text", False, None),
            ("prescribed_medicines", "Prescribed Medicines", "text", False, None),
            ("doctor_notes", "Doctor Notes", "text", False, None),
            ("follow_up_required", "Follow Up Required", "text", True, None),
            ("follow_up_date", "Follow Up Date", "text", False, None),
            ("next_visit_reason", "Next Visit Reason", "text", False, None),
        ]
    }

    # 3. Define Relationships
    relationships_data = [
        ("visit", "patient", "many_to_one", "patient_id", "id", True),
        ("visit", "user", "many_to_one", "doctor_id", "id", False),
        ("prescription", "visit", "many_to_one", "visit_id", "id", True),
        ("prescription", "medicine", "many_to_one", "medicine_id", "id", False),
        ("inventory", "medicine", "one_to_one", "medicine_id", "id", True),
        ("inventory_transaction", "inventory", "many_to_one", "inventory_id", "id", True),
        ("laboratory", "patient", "many_to_one", "patient_id", "id", True),
        ("laboratory", "visit", "many_to_one", "visit_id", "id", True),
        ("laboratory", "user", "many_to_one", "lab_technician_id", "id", False),
        ("laboratory", "user", "many_to_one", "requested_by", "id", False),
        ("lab_report", "laboratory", "many_to_one", "lab_id", "id", True),
        ("lab_report", "lab_test_catalog", "many_to_one", "test_id", "id", False),
        ("lab_report", "patient", "many_to_one", "patient_id", "id", True),
        ("lab_report", "user", "many_to_one", "doctor_id", "id", False),
        ("lab_report", "user", "many_to_one", "verified_by", "id", False),
        ("report", "visit", "many_to_one", "visit_id", "id", True),
        ("report", "patient", "many_to_one", "patient_id", "id", True),
    ]

    # Seed Modules
    modules_by_api_name = {}
    for api_name, (name, plural_label, desc) in modules_data.items():
        mod = db.session.query(Module).filter_by(id=api_name).first()
        if not mod:
            mod = Module(
                id=api_name,
                tenant_id=tenant_id,
                org_id=org_id,
                created_by=user_id,
                updated_by=user_id,
                name=name,
                api_name=api_name,
                label=name,
                plural_label=plural_label,
                description=desc,
                is_system=False
            )
            db.session.add(mod)
            db.session.flush()
        modules_by_api_name[api_name] = mod

    # Seed Fields
    for api_name, fields in fields_data.items():
        module = modules_by_api_name[api_name]
        existing_fields = db.session.query(Field).filter_by(module_id=module.id).all()
        assigned_cols = {f.api_name: f.column_name for f in existing_fields}
        
        col_idx = 1
        for f_api_name, f_name, f_type, is_req, lookup_id in fields:
            f_orm = db.session.query(Field).filter_by(module_id=module.id, api_name=f_api_name).first()
            if not f_orm:
                while f"column_{col_idx}" in assigned_cols.values():
                    col_idx += 1
                import uuid
                f_orm = Field(
                    id=uuid.uuid4().hex[:32],
                    tenant_id=tenant_id,
                    org_id=org_id,
                    created_by=user_id,
                    updated_by=user_id,
                    module_id=module.id,
                    field_name=f_name,
                    api_name=f_api_name,
                    field_type=f_type,
                    label=f_name,
                    is_required=is_req,
                    is_unique=False,
                    column_name=f"column_{col_idx}",
                    lookup_module_id=lookup_id
                )
                db.session.add(f_orm)
                db.session.flush()
                assigned_cols[f_api_name] = f_orm.column_name
                col_idx += 1

    # Seed Relationships
    for from_api, to_api, rel_type, from_field, to_field, cascade in relationships_data:
        from_mod = modules_by_api_name[from_api]
        to_mod = modules_by_api_name[to_api]
        rel = db.session.query(RelationshipDefinition).filter_by(
            from_module_id=from_mod.id,
            to_module_id=to_mod.id,
            from_field_name=from_field
        ).first()
        if not rel:
            import uuid
            rel = RelationshipDefinition(
                id=uuid.uuid4().hex[:32],
                tenant_id=tenant_id,
                org_id=org_id,
                created_by=user_id,
                updated_by=user_id,
                from_module_id=from_mod.id,
                to_module_id=to_mod.id,
                relationship_type=rel_type,
                from_field_name=from_field,
                to_field_name=to_field,
                cascade_delete=cascade
            )
            db.session.add(rel)
            
    # Seed default roles
    roles_list = ["ADMIN", "DOCTOR", "LAB_TECHNICIAN", "PHARMACIST", "RECEPTIONIST", "NURSE"]
    role_module = modules_by_api_name["role"]
    from hogc.engines.crud.schema.record import Record
    field_name = db.session.query(Field).filter_by(module_id=role_module.id, api_name="name").first()
    if field_name:
        for role_name in roles_list:
            rec_exist = db.session.query(Record).filter(
                Record.module_id == role_module.id,
                getattr(Record, field_name.column_name) == role_name
            ).first()
            if not rec_exist:
                import uuid
                r_rec = Record(
                    id=uuid.uuid4().hex[:32],
                    tenant_id=tenant_id,
                    org_id=org_id,
                    created_by=user_id,
                    updated_by=user_id,
                    module_id=role_module.id,
                )
                setattr(r_rec, field_name.column_name, role_name)
                db.session.add(r_rec)

    db.session.commit()
