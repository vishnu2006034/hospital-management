"""Authentication service for business logic using hogc-crud-engine."""

import random
from datetime import datetime
from typing import Dict, List, Optional
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import UserSession, crud_provider
from app.dtos.user import UserResponse
from app.services.interfaces.auth_service_interface import IAuthService
from app.services.crud_helper import run_in_context, query_records
from hogc.lib.contracts.crud.requests import CreateRecordRequest, GetRecordRequest

class AuthService(IAuthService):
    """Service layer for Authentication business operations using hogc-crud-engine."""

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[UserResponse]:
        """Authenticate a user by email and password."""
        def action(ctx) -> Optional[UserResponse]:
            resp = query_records(ctx, "user", {"email": email.strip().lower()})
            if not resp.items:
                return None
            rec = resp.items[0]
            pwd_hash = rec.data.get("password_hash")
            if not pwd_hash or not check_password_hash(pwd_hash, password):
                return None
            
            return UserResponse(
                user_id=rec.id,
                employee_code=rec.data.get("employee_code", "EMP-0000"),
                first_name=rec.data.get("first_name", ""),
                last_name=rec.data.get("last_name"),
                email=rec.data.get("email"),
                status=rec.data.get("status", "ACTIVE"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                full_name=f"{rec.data.get('first_name', '')} {rec.data.get('last_name', '')}".strip(),
                role_names=[rec.data.get("role")] if rec.data.get("role") else []
            )
        return run_in_context(action)

    @staticmethod
    def login(user: UserResponse, remember: bool = False) -> None:
        def action(ctx) -> None:
            req = GetRecordRequest(context=ctx, module_id="user", record_id=user.user_id)
            resp = crud_provider.records.get_record(req)
            rec = resp.data
            user_session = UserSession(
                user_id=rec.id,
                email=rec.data.get("email"),
                first_name=rec.data.get("first_name"),
                last_name=rec.data.get("last_name"),
                status=rec.data.get("status", "ACTIVE"),
                role=rec.data.get("role"),
                password_hash=rec.data.get("password_hash")
            )
            login_user(user_session, remember=remember)
        run_in_context(action)

    @staticmethod
    def logout() -> None:
        logout_user()

    @staticmethod
    def validate_registration(data: Dict[str, str]) -> List[str]:
        """Validate registration data."""
        errors: List[str] = []
        if not data.get('first_name'):
            errors.append('First name is required.')
        if not data.get('email'):
            errors.append('Email is required.')
        if not data.get('password'):
            errors.append('Password is required.')
        if data.get('password') != data.get('confirm_password'):
            errors.append('Passwords do not match.')
        if len(data.get('password', '')) < 6:
            errors.append('Password must be at least 6 characters.')
            
        def check_exists(ctx) -> bool:
            resp = query_records(ctx, "user", {"email": data.get('email', '').strip().lower()})
            return len(resp.items) > 0
            
        if run_in_context(check_exists):
            errors.append('An account with this email already exists.')
        return errors

    @staticmethod
    def generate_employee_code() -> str:
        return f"EMP-{random.randint(1000, 9999)}"

    @staticmethod
    def create_user(data: Dict[str, str]) -> UserResponse:
        """Create a new user account."""
        email = data['email'].strip().lower()
        password_hash = generate_password_hash(data['password'])
        emp_code = AuthService.generate_employee_code()
        
        def action(ctx) -> UserResponse:
            record_data = {
                "first_name": data['first_name'].strip(),
                "last_name": data.get('last_name', '').strip() if data.get('last_name') else None,
                "email": email,
                "password_hash": password_hash,
                "status": "ACTIVE",
                "role": data.get('role', 'STAFF'),
                "employee_code": emp_code
            }
            req = CreateRecordRequest(
                context=ctx,
                module_id="user",
                data=record_data
            )
            resp = crud_provider.records.create_record(req)
            rec = resp.data
            
            return UserResponse(
                user_id=rec.id,
                employee_code=emp_code,
                first_name=rec.data.get("first_name"),
                last_name=rec.data.get("last_name"),
                email=rec.data.get("email"),
                status=rec.data.get("status"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                full_name=f"{rec.data.get('first_name', '')} {rec.data.get('last_name', '')}".strip(),
                role_names=[rec.data.get("role")] if rec.data.get("role") else []
            )
        return run_in_context(action)
