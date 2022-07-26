from pydantic import BaseModel, EmailStr


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class UserRegisterIn(BaseRequest):  # OK
    email: EmailStr
    password: str
    password_confirmation: str
    tos: bool
    tz: str | None = "Europe/Warsaw"
    lang: str | None = "pl"


class UserFirstRunIn(BaseRequest):  # OK
    first_name: str
    last_name: str
    nip: str = "1234563218"
    token: str


class UserLoginIn(BaseRequest):  # OK
    email: EmailStr
    password: str
    permanent: bool
