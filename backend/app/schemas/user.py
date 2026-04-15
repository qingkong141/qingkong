from app.schemas.base import BaseSchema


class ChangePasswordRequest(BaseSchema):
    # old_password → oldPassword，new_password → newPassword
    old_password: str
    new_password: str
