"""Staff service for business logic using hogc-crud-engine."""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from werkzeug.security import generate_password_hash

from app.dtos.user import UserResponse, RoleResponse, UserRoleResponse
from app.extensions import crud_provider
from app.services.interfaces.staff_service_interface import IStaffService
from app.services.crud_helper import run_in_context, query_records, EAVPagination
from hogc.lib.contracts.crud.requests import CreateRecordRequest, GetRecordRequest, UpdateRecordRequest, ListRecordsRequest
from app.utils import clean_input_data

class StaffService(IStaffService):
    """Service layer for Staff (User) business operations using hogc-crud-engine."""

    @staticmethod
    def map_to_staff(rec) -> UserResponse:
        dob = None
        dob_str = rec.data.get("dob")
        if dob_str:
            try:
                dob = datetime.strptime(dob_str[:10], "%Y-%m-%d").date()
            except Exception:
                pass
                
        joining_date = None
        jd_str = rec.data.get("joining_date")
        if jd_str:
            try:
                joining_date = datetime.strptime(jd_str[:10], "%Y-%m-%d").date()
            except Exception:
                pass

        return UserResponse(
            user_id=rec.id,
            employee_code=rec.data.get("employee_code", "EMP-0000"),
            first_name=rec.data.get("first_name", ""),
            last_name=rec.data.get("last_name"),
            gender=rec.data.get("gender"),
            dob=dob,
            phone=rec.data.get("phone"),
            email=rec.data.get("email"),
            department=rec.data.get("department"),
            specialization=rec.data.get("specialization"),
            license_number=rec.data.get("license_number"),
            joining_date=joining_date,
            status=rec.data.get("status", "ACTIVE"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            full_name=f"{rec.data.get('first_name', '')} {rec.data.get('last_name', '')}".strip(),
            role_names=[rec.data.get("role")] if rec.data.get("role") else []
        )

    @staticmethod
    def get_staff_by_id(user_id: str) -> Optional[UserResponse]:
        """Convenience method to retrieve user response directly by ID."""
        def action(ctx) -> UserResponse:
            req = GetRecordRequest(context=ctx, module_id="user", record_id=user_id)
            resp = crud_provider.records.get_record(req)
            return StaffService.map_to_staff(resp.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[UserResponse]:
        """Get a user by ID."""
        return StaffService.get_staff_by_id(user_id)

    @staticmethod
    def get_all_staff(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> EAVPagination:
        """Get paginated list of staff members."""
        def action(ctx) -> EAVPagination:
            if search:
                req = ListRecordsRequest(context=ctx, module_id="user", page=1, page_size=1000)
                resp = crud_provider.records.list_records(req)
                all_items = [StaffService.map_to_staff(r) for r in resp.items]
                s = search.lower().strip()
                filtered = [
                    x for x in all_items
                    if s in x.first_name.lower()
                    or (x.last_name and s in x.last_name.lower())
                    or (x.employee_code and s in x.employee_code.lower())
                    or (x.email and s in x.email.lower())
                ]
                total = len(filtered)
                start = (page - 1) * per_page
                end = start + per_page
                items = filtered[start:end]
                return EAVPagination(items, page, per_page, total)
            else:
                req = ListRecordsRequest(context=ctx, module_id="user", page=page, page_size=per_page)
                resp = crud_provider.records.list_records(req)
                items = [StaffService.map_to_staff(r) for r in resp.items]
                return EAVPagination(items, page, per_page, resp.total)
        return run_in_context(action)

    @staticmethod
    def generate_employee_code() -> str:
        import random
        return f"EMP-{random.randint(1000, 9999)}"

    @staticmethod
    def create_staff(data: Dict[str, Any]) -> UserResponse:
        """Create a new staff member."""
        cleaned = clean_input_data(data)
        emp_code = StaffService.generate_employee_code()
        
        dob_val = cleaned.get("dob")
        if isinstance(dob_val, (date, datetime)):
            dob_val = dob_val.strftime("%Y-%m-%d")
            
        jd_val = cleaned.get("joining_date")
        if isinstance(jd_val, (date, datetime)):
            jd_val = jd_val.strftime("%Y-%m-%d")

        role_name = "STAFF"
        role_id_val = cleaned.get("role_id")
        if role_id_val:
            role_dto = StaffService.get_role_by_id(str(role_id_val))
            if role_dto:
                role_name = role_dto.role_name

        record_data = {
            "first_name": cleaned['first_name'],
            "last_name": cleaned.get('last_name'),
            "email": cleaned['email'].strip().lower(),
            "password_hash": generate_password_hash(cleaned['password']) if cleaned.get('password') else generate_password_hash("password123"),
            "gender": cleaned.get('gender'),
            "dob": dob_val,
            "phone": cleaned.get('phone'),
            "department": cleaned.get('department'),
            "specialization": cleaned.get('specialization'),
            "license_number": cleaned.get('license_number'),
            "joining_date": jd_val,
            "status": cleaned.get('status') or 'ACTIVE',
            "role": role_name,
            "employee_code": emp_code
        }

        def action(ctx) -> UserResponse:
            req = CreateRecordRequest(context=ctx, module_id="user", data=record_data)
            resp = crud_provider.records.create_record(req)
            return StaffService.map_to_staff(resp.data)
        return run_in_context(action)

    @staticmethod
    def update_staff(user_id: str, data: Dict[str, Any]) -> Optional[UserResponse]:
        """Update an existing staff member."""
        cleaned = clean_input_data(data)
        
        dob_val = cleaned.get("dob")
        if isinstance(dob_val, (date, datetime)):
            dob_val = dob_val.strftime("%Y-%m-%d")
            
        jd_val = cleaned.get("joining_date")
        if isinstance(jd_val, (date, datetime)):
            jd_val = jd_val.strftime("%Y-%m-%d")

        def action(ctx) -> UserResponse:
            req_get = GetRecordRequest(context=ctx, module_id="user", record_id=user_id)
            resp_get = crud_provider.records.get_record(req_get)
            current_data = resp_get.data.data
            
            editable_fields = (
                "first_name",
                "last_name",
                "gender",
                "phone",
                "email",
                "department",
                "specialization",
                "license_number",
            )
            for field in editable_fields:
                if field in cleaned:
                    current_data[field] = str(cleaned[field]) if cleaned[field] is not None else None
            
            if "dob" in cleaned:
                current_data["dob"] = dob_val
            if "joining_date" in cleaned:
                current_data["joining_date"] = jd_val
            if "status" in cleaned:
                current_data["status"] = cleaned["status"]
            if "password" in cleaned and cleaned["password"]:
                current_data["password_hash"] = generate_password_hash(cleaned["password"])

            req_up = UpdateRecordRequest(context=ctx, record_id=user_id, module_id="user", data=current_data)
            resp_up = crud_provider.records.update_record(req_up)
            return StaffService.map_to_staff(resp_up.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def get_user_roles(user_id: str) -> List[UserRoleResponse]:
        """Get all role assignments for a user."""
        user = StaffService.get_staff_by_id(user_id)
        if not user:
            return []
        roles = StaffService.get_all_roles()
        role_id = ""
        for r in roles:
            if r.role_name in user.role_names:
                role_id = r.role_id
                break
        return [UserRoleResponse(role_id=role_id, role_name=r_name, is_active=True) for r_name in user.role_names]

    @staticmethod
    def toggle_role(user_id: str, role_id: str) -> str:
        """Toggle a role's active status for a user."""
        role_dto = StaffService.get_role_by_id(role_id)
        if not role_dto:
            return "deassigned"
            
        def action(ctx) -> str:
            req_get = GetRecordRequest(context=ctx, module_id="user", record_id=user_id)
            resp_get = crud_provider.records.get_record(req_get)
            current_data = resp_get.data.data
            
            current_role = current_data.get("role")
            if current_role == role_dto.role_name:
                current_data["role"] = None
                action_performed = "deassigned"
            else:
                current_data["role"] = role_dto.role_name
                action_performed = "assigned"
                
            req_up = UpdateRecordRequest(context=ctx, record_id=user_id, module_id="user", data=current_data)
            crud_provider.records.update_record(req_up)
            return action_performed
        return run_in_context(action)

    @staticmethod
    def get_all_roles() -> List[RoleResponse]:
        """Get all available roles."""
        def action(ctx) -> List[RoleResponse]:
            req = ListRecordsRequest(context=ctx, module_id="role", page=1, page_size=100)
            resp = crud_provider.records.list_records(req)
            return [
                RoleResponse(role_id=r.id, role_name=r.data.get("name", ""))
                for r in resp.items
            ]
        return run_in_context(action)

    @staticmethod
    def get_role_by_id(role_id: str) -> Optional[RoleResponse]:
        """Get a role by ID."""
        def action(ctx) -> RoleResponse:
            req = GetRecordRequest(context=ctx, module_id="role", record_id=role_id)
            resp = crud_provider.records.get_record(req)
            return RoleResponse(role_id=resp.data.id, role_name=resp.data.data.get("name", ""))
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def get_active_doctors_count() -> int:
        """Count active doctors."""
        def action(ctx) -> int:
            resp = query_records(ctx, "user", {"role": "DOCTOR", "status": "ACTIVE"}, page=1, page_size=1)
            return resp.total
        return run_in_context(action)
