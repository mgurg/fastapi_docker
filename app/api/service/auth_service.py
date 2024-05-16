from typing import Annotated

from fastapi import Depends

from app.api.repository.PublicCompanyRepo import PublicCompanyRepo
from app.api.repository.PublicUserRepo import PublicUserRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo


class AuthService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends()],
        role_repo: Annotated[RoleRepo, Depends()],
        public_user_repo: Annotated[PublicUserRepo, Depends()],
        public_company_repo: Annotated[PublicCompanyRepo, Depends()],
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.public_user_repo = public_user_repo
        self.public_company_repo = public_company_repo

    def get_limit(self):
        return self.public_company_repo.get_users_count()
