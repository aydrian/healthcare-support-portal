from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# User schemas
class UserBase(BaseModel):
    username: str
    email: str
    role: str
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime

# Patient schemas
class PatientBase(BaseModel):
    name: str
    medical_record_number: str
    department: Optional[str] = None

class PatientCreate(PatientBase):
    assigned_doctor_id: Optional[int] = None

class PatientResponse(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assigned_doctor_id: Optional[int]
    is_active: bool
    created_at: datetime

# Document schemas
class DocumentBase(BaseModel):
    title: str
    content: str
    document_type: str
    department: Optional[str] = None
    is_sensitive: bool = False

class DocumentCreate(DocumentBase):
    patient_id: Optional[int] = None

class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: Optional[int]
    created_by_id: int
    created_at: datetime

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
