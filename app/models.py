from sqlmodel import SQLModel, Field, Column, String, Relationship, Text
from datetime import datetime, timezone
import sqlalchemy.dialects.postgresql as pg
import uuid
from typing import Optional, List
from enum import Enum



class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    EDITOR = "editor"

# USERS
class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    email: str = Field(nullable=False)
    password: str = Field(nullable=False) 
    # temporary_password: str = Field(nullable=True)
    phone_number: str = Field(nullable=True)
    role: UserRole = Field(sa_column=Column(String, default=UserRole.USER.value))
    is_verified: bool = Field(default=False)
    is_premium: bool = Field(default=False)
    created_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now, nullable=False))
    updated_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now))
    
    courses: List['Course'] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy":"selectin"})

    def __repr__(self):
        return f"<User {self.first_name} | Role {self.role}>"


# TAG
class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int = Field(default=None, primary_key=True) 
    name: str = Column(unique=True, nullable=False)

    courses: List['Course'] = Relationship(back_populates="tags", sa_relationship_kwargs={"lazy":"selectin", "secondary": "course_tags"}) 

    def __repr__(self):
        return f"<Tag {self.name}>"


#VIDEO COURSE
class Course(SQLModel, table=True):
    __tablename__ = "courses"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(nullable=False) 
    thumbnail: str = Field(nullable=True) 
    description: str = Field(nullable=True)
    
    courses: Optional[dict] = Field(sa_column=Column("courses", pg.JSONB(astext_type=Text())))
    created_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now, nullable=False))
    updated_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now, onupdate=datetime.now)) 
    user_uid: uuid.UUID = Field(foreign_key="users.uid")

    user: Optional['User'] = Relationship(back_populates="courses", sa_relationship_kwargs={"lazy":"selectin"})
    tags: List['Tag'] = Relationship(back_populates="courses", sa_relationship_kwargs={"lazy":"selectin", "secondary": "course_tags"})

    def __repr__(self):
        return f"<Video Course {self.title}>"

class CourseTag(SQLModel, table=True):
    __tablename__ = "course_tags"

    course_uid: uuid.UUID = Field(primary_key=True, foreign_key='courses.uid')
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)

    def __repr__(self):
        return f"<Course Uid {self.course_uid} has tag {self.tag_id}>"


# TOKEN
class RevokedToken(SQLModel, table=True):
    __tablename__="revokedtoken"
    tokenid: uuid.UUID = Field(
        sa_column= Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    token_jti : str = Field(sa_column= Column(String(300), primary_key=True))

    def __repr__(self):
        return f"<Token {self.token_jti}>"
    