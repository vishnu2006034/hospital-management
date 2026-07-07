from typing import Optional, List
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.dtos.user import UserResponse, UserCreateRequest, UserUpdateRequest, RoleResponse, UserRoleResponse

class UserMapper:
    @staticmethod
    def to_dto(user: User) -> UserResponse:
        if not user:
            return None
        return UserResponse(
            user_id=user.user_id,
            employee_code=user.employee_code,
            first_name=user.first_name,
            last_name=user.last_name,
            gender=user.gender,
            dob=user.dob,
            phone=user.phone,
            email=user.email,
            department=user.department,
            specialization=user.specialization,
            license_number=user.license_number,
            joining_date=user.joining_date,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            full_name=user.full_name,
            role_names=user.role_names
        )

    @staticmethod
    def to_model(dto: UserCreateRequest) -> User:
        user = User()
        user.first_name = dto.first_name
        user.last_name = dto.last_name
        user.email = dto.email
        user.gender = dto.gender
        user.dob = dto.dob
        user.phone = dto.phone
        user.department = dto.department
        user.specialization = dto.specialization
        user.license_number = dto.license_number
        user.joining_date = dto.joining_date
        user.status = dto.status or "ACTIVE"
        user.password = dto.password
        return user

    @staticmethod
    def update_model(user: User, dto: UserUpdateRequest) -> User:
        user.first_name = dto.first_name
        user.last_name = dto.last_name
        user.email = dto.email
        user.gender = dto.gender
        user.dob = dto.dob
        user.phone = dto.phone
        user.department = dto.department
        user.specialization = dto.specialization
        user.license_number = dto.license_number
        user.joining_date = dto.joining_date
        if dto.status:
            user.status = dto.status
        if dto.password:
            user.password = dto.password
        return user

    @staticmethod
    def to_role_dto(role: Role) -> RoleResponse:
        if not role:
            return None
        return RoleResponse(
            role_id=role.role_id,
            role_name=role.role_name
        )

    @staticmethod
    def to_user_role_dto(ur: UserRole) -> UserRoleResponse:
        if not ur:
            return None
        return UserRoleResponse(
            role_id=ur.role_id,
            role_name=ur.role.role_name if ur.role else "",
            is_active=ur.is_active
        )
