from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[str]
    username: str
    full_name: str
    email: str
    permission: str
    role: str
    disabled: bool

class UserDB(User):
    password: str