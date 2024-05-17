from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.models.models import User


class ACL:
    def __init__(self, user: User):
        self.user = user
        self.user_permissions = self._get_user_permissions()

    def _get_user_permissions(self) -> list[str]:
        """Private method to get user permissions."""
        return [permission.name for permission in self.user.role_FK.permission]

    def required(self, required_acl: str | None = None) -> bool:
        """Public method to check if the user has the required ACL."""
        if required_acl and required_acl not in self.user_permissions:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail=f"Insufficient permissions, require acl: {required_acl}"
            )
        return True

    def no_required(self) -> bool:
        return True


# Usage
# Assuming you have a user object from your database
# user = <fetch user from the database>
