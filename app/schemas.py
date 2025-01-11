from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# USERS
class UserModel(BaseModel):
    uid: uuid.UUID
    email: str
    password: str 
    first_name: str
    last_name: str
    phone_number: str
    is_premium: bool

class UserCreateModel(BaseModel):
    email: str
    password: str 
    first_name: str
    last_name: str

class UserUpdateModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    is_premium: Optional[bool] = None

class UserResponseModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    is_verified: bool
    is_premium: bool
    role: str

class AdminEditorResponseProfileModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    is_verified: bool
    is_premium: bool
    role: str
    courses: List['Course']

class UserResponseModelProfile(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: str

class UserLoginModel(BaseModel):
    email: str
    password: str 

  
# ADMIN
class Admin(BaseModel):
    uid: uuid.UUID 
    email: str
    password: str = Field(exclude=True)
    first_name: str
    last_name: str
    phone_number: str
    is_verified: bool = False
    created_at: datetime 
    updated_at: datetime 
    role: str

class AdminCreateModel(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class AdminCreateUserModel(BaseModel):
    email: str
    password: Optional[str] = None 
    first_name: str
    last_name: str

class AdminUpdateModel(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None


class AdminLoginModel(BaseModel):
    email: str
    password: str 

class AdminResponseModel(BaseModel):
    email: str
    first_name: str

class AdminProfileModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    role: str


# COURSES
class Course(BaseModel):
    uid: uuid.UUID 
    title: str 
    thumbnail: Optional[str] 
    description: Optional[str]
    courses: dict
    created_at: datetime 
    updated_at: datetime 
    user_uid: uuid.UUID 
    tags: List['TagResponseModel']
    

class CourseCreateModel(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    courses: dict
    tags: List[str]

class CourseUpdateModel(BaseModel):
    title: Optional[str] = None
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    courses: Optional[dict] = None
    tags: List[str] = None

class CourseResponseModel(BaseModel):
    uid: uuid.UUID
    title: str 
    thumbnail: Optional[str] 
    description: Optional[str]
    courses: dict
    created_at: datetime 
    updated_at: datetime 
    user: Optional['UserResponseModelProfile']
    tags: List['TagResponseModel']


# TAGS
class Tag(BaseModel):
    name: str

class TagModel(Tag):
    pass

class TagResponseModel(BaseModel):
    id: int
    name: str

# TOKEN

class RevokedTokenModel(BaseModel):
    token_jti: str


# EMAIL MODELS

class EmailModel(BaseModel):
    addresses: List[str]
