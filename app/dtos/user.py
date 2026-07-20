from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    role_id: str
    role_name: str

class UserRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    role_id: str
    role_name: str
    is_active: bool

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    employee_code: str
    first_name: str
    last_name: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    joining_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Extra properties to match SQLAlchemy model convenience properties
    full_name: str
    role_names: List[str] = Field(default_factory=list)

    def has_role(self, role_name: str) -> bool:
        return role_name in self.role_names

class UserCreateRequest(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: str
    role: Optional[str] = None
    password: str
    gender: Optional[str] = None
    dob: Optional[date] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    joining_date: Optional[date] = None
    status: Optional[str] = "ACTIVE"
    role_id: Optional[str] = None

class UserUpdateRequest(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: str
    gender: Optional[str] = None
    dob: Optional[date] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    joining_date: Optional[date] = None
    status: Optional[str] = None
    password: Optional[str] = None
