from pydantic import BaseModel, ConfigDict, Field


### Requests ###

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


### Responses ###

class Token(BaseModel):
    access_token: str
    token_type: str


class TodoResponse(BaseModel):
    # Lets Pydantic read values from ORM object attributes, not only from dicts
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    priority: int
    complete: bool
    owner_id: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Whitelist of fields sent to clients; hashed_password is intentionally absent
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    phone_number: str | None  # column was added by migration as nullable
    is_active: bool
