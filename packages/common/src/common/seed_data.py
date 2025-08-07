#!/usr/bin/env python3
"""
Database seeding script for Healthcare Support Portal
Creates demo users, patients, and documents for development and demonstration.

This script is idempotent - safe to run multiple times without creating duplicates.
"""

import sys
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session

from .db import SessionLocal, enable_extensions, create_tables
from .models import User, Patient, Document
from .auth import get_password_hash


def seed_users(db: Session) -> Dict[str, User]:
    """Create demo users if they don't exist."""
    created_users = {}
    demo_users = [
        {
            "username": "dr_smith",
            "email": "sarah.smith@hospital.com",
            "password": "secure_password",
            "role": "doctor",
            "department": "cardiology",
            "full_name": "Dr. Sarah Smith"
        },
        {
            "username": "nurse_johnson",
            "email": "michael.johnson@hospital.com", 
            "password": "secure_password",
            "role": "nurse",
            "department": "emergency",
            "full_name": "Nurse Michael Johnson"
        },
        {
            "username": "admin_wilson",
            "email": "jennifer.wilson@hospital.com",
            "password": "secure_password", 
            "role": "admin",
            "department": "administration",
            "full_name": "Admin Jennifer Wilson"
        }
    ]
    
    for user_data in demo_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if existing_user:
            print(f"✅ User '{user_data['username']}' already exists, skipping")
            created_users[user_data["username"]] = existing_user
            continue
            
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_email:
            print(f"⚠️  Email '{user_data['email']}' already exists, skipping user '{user_data['username']}'")
            continue
        
        # Create new user
        hashed_password = get_password_hash(user_data["password"])
        new_user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            role=user_data["role"],
            department=user_data["department"],
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        created_users[user_data["username"]] = new_user
        print(f"✅ Created user: {user_data['full_name']} ({user_data['username']})")
    
    return created_users


def seed_patients(db: Session, users: Dict[str, User]) -> List[Patient]:
    """Create demo patients if they don't exist."""
    created_patients = []
    
    # Get the doctor user
    doctor = users.get("dr_smith")
    if not doctor:
        print("⚠️  Doctor user not found, skipping patient creation")
        return created_patients
    
    demo_patients = [
        {
            "name": "John Anderson",
            "medical_record_number": "MRN-2024-001",
            "department": "cardiology",
            "date_of_birth": datetime(1965, 3, 15)
        },
        {
            "name": "Maria Rodriguez",
            "medical_record_number": "MRN-2024-002", 
            "department": "cardiology",
            "date_of_birth": datetime(1978, 8, 22)
        },
        {
            "name": "Robert Chen",
            "medical_record_number": "MRN-2024-003",
            "department": "cardiology", 
            "date_of_birth": datetime(1952, 11, 8)
        }
    ]
    
    for patient_data in demo_patients:
        # Check if patient already exists
        existing_patient = db.query(Patient).filter(
            Patient.medical_record_number == patient_data["medical_record_number"]
        ).first()
        if existing_patient:
            print(f"✅ Patient '{patient_data['name']}' (MRN: {patient_data['medical_record_number']}) already exists, skipping")
            created_patients.append(existing_patient)
            continue
        
        # Create new patient
        new_patient = Patient(
            name=patient_data["name"],
            medical_record_number=patient_data["medical_record_number"],
            department=patient_data["department"],
            date_of_birth=patient_data["date_of_birth"],
            assigned_doctor_id=doctor.id,
            is_active=True
        )
        
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        created_patients.append(new_patient)
        print(f"✅ Created patient: {patient_data['name']} (MRN: {patient_data['medical_record_number']})")
    
    return created_patients


def seed_documents(db: Session, users: Dict[str, User], patients: List[Patient]) -> List[Document]:
    """Create demo documents if they don't exist."""
    created_documents = []
    
    # Get the doctor user
    doctor = users.get("dr_smith")
    if not doctor:
        print("⚠️  Doctor user not found, skipping document creation")
        return created_documents
    
    demo_documents = [
        {
            "title": "Cardiology Department Protocols",
            "content": """# Cardiology Department Standard Operating Procedures

## Patient Assessment Protocols
1. Initial cardiac risk assessment for all new patients
2. ECG interpretation guidelines and red flags
3. Chest pain evaluation protocols
4. Heart failure management guidelines

## Diagnostic Procedures
- Echocardiogram ordering criteria
- Stress test indications and contraindications
- Cardiac catheterization preparation protocols
- Post-procedure monitoring requirements

## Medication Management
- ACE inhibitor dosing and monitoring
- Beta-blocker titration protocols
- Anticoagulation management
- Drug interaction guidelines

## Emergency Procedures
- Code Blue response protocols
- Cardiac arrest management
- Acute MI treatment pathways
- Arrhythmia management protocols

Last updated: January 2024""",
            "document_type": "protocol",
            "department": "cardiology",
            "is_sensitive": False
        },
        {
            "title": "Hypertension Management Guidelines",
            "content": """# Hypertension Management Guidelines

## Classification
- Normal: <120/80 mmHg
- Elevated: 120-129/<80 mmHg  
- Stage 1: 130-139/80-89 mmHg
- Stage 2: ≥140/≥90 mmHg
- Crisis: >180/>120 mmHg

## Initial Assessment
1. Confirm diagnosis with multiple readings
2. Assess for secondary causes
3. Evaluate cardiovascular risk factors
4. Screen for target organ damage

## Treatment Approach
### Lifestyle Modifications
- DASH diet implementation
- Sodium restriction (<2.3g/day)
- Weight management (BMI <25)
- Regular aerobic exercise (150 min/week)
- Alcohol moderation
- Smoking cessation

### Pharmacological Treatment
First-line agents:
- ACE inhibitors or ARBs
- Calcium channel blockers
- Thiazide diuretics

## Monitoring
- BP checks every 2-4 weeks during titration
- Annual lab work (creatinine, potassium)
- Yearly cardiovascular risk assessment

Target: <130/80 mmHg for most patients""",
            "document_type": "guideline",
            "department": "cardiology",
            "is_sensitive": False
        },
        {
            "title": "Heart Failure Patient Education",
            "content": """# Heart Failure: Patient Education Guide

## What is Heart Failure?
Heart failure occurs when your heart cannot pump blood effectively to meet your body's needs. This doesn't mean your heart has stopped working, but rather that it needs support to work better.

## Common Symptoms
- Shortness of breath (especially when lying down)
- Fatigue and weakness
- Swelling in legs, ankles, or feet
- Rapid or irregular heartbeat
- Persistent cough or wheezing
- Weight gain from fluid retention

## Daily Management
### Medications
- Take all medications as prescribed
- Never skip doses
- Know your medications and their purposes
- Report side effects to your healthcare team

### Diet and Fluid Management
- Limit sodium intake (less than 2 grams daily)
- Monitor fluid intake as directed
- Weigh yourself daily at the same time
- Call if weight increases by 2-3 pounds in one day

### Activity Guidelines
- Stay active within your limits
- Pace yourself and rest when needed
- Avoid sudden increases in activity
- Participate in cardiac rehabilitation if recommended

## When to Call Your Doctor
- Weight gain of 2-3 pounds in one day
- Increased shortness of breath
- New or worsening swelling
- Chest pain or discomfort
- Dizziness or fainting
- Any concerns about your condition

Remember: You are an important part of your healthcare team!""",
            "document_type": "education",
            "department": "cardiology", 
            "is_sensitive": False
        }
    ]
    
    for doc_data in demo_documents:
        # Check if document already exists (by title)
        existing_doc = db.query(Document).filter(
            Document.title == doc_data["title"]
        ).first()
        if existing_doc:
            print(f"✅ Document '{doc_data['title']}' already exists, skipping")
            created_documents.append(existing_doc)
            continue
        
        # Create new document
        new_document = Document(
            title=doc_data["title"],
            content=doc_data["content"],
            document_type=doc_data["document_type"],
            department=doc_data["department"],
            created_by_id=doctor.id,
            is_sensitive=doc_data["is_sensitive"]
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        created_documents.append(new_document)
        print(f"✅ Created document: {doc_data['title']}")
    
    # Create patient-specific documents
    if patients:
        patient_docs = [
            {
                "title": f"Medical History - {patients[0].name}",
                "content": f"""# Medical History for {patients[0].name}
MRN: {patients[0].medical_record_number}

## Chief Complaint
Routine cardiac follow-up for hypertension and coronary artery disease.

## History of Present Illness
67-year-old male with history of hypertension, hyperlipidemia, and prior MI in 2020. Currently stable on optimal medical therapy. Reports good exercise tolerance and no chest pain.

## Past Medical History
- Hypertension (2015)
- Hyperlipidemia (2016)
- ST-elevation myocardial infarction (2020)
- Percutaneous coronary intervention with drug-eluting stent to LAD (2020)

## Current Medications
- Metoprolol succinate 50mg daily
- Lisinopril 10mg daily
- Atorvastatin 80mg daily
- Aspirin 81mg daily
- Clopidogrel 75mg daily

## Allergies
No known drug allergies

## Social History
Former smoker (quit 2020), occasional alcohol use, married, retired electrician.

## Assessment and Plan
Stable coronary artery disease. Continue current medications. Next follow-up in 6 months with stress test if symptoms develop.""",
                "document_type": "medical_record",
                "patient_id": patients[0].id,
                "is_sensitive": True
            }
        ]
        
        for doc_data in patient_docs:
            # Check if patient document already exists
            existing_doc = db.query(Document).filter(
                Document.title == doc_data["title"],
                Document.patient_id == doc_data["patient_id"]
            ).first()
            if existing_doc:
                print(f"✅ Patient document '{doc_data['title']}' already exists, skipping")
                continue
            
            # Create new patient document
            new_document = Document(
                title=doc_data["title"],
                content=doc_data["content"],
                document_type=doc_data["document_type"],
                department="cardiology",
                patient_id=doc_data["patient_id"],
                created_by_id=doctor.id,
                is_sensitive=doc_data["is_sensitive"]
            )
            
            db.add(new_document)
            db.commit()
            db.refresh(new_document)
            
            created_documents.append(new_document)
            print(f"✅ Created patient document: {doc_data['title']}")
    
    return created_documents


def main() -> None:
    """Main seeding function."""
    print("🌱 Healthcare Support Portal - Database Seeding")
    print("=" * 50)
    
    try:
        # Ensure database extensions and tables exist
        print("📊 Ensuring database schema is up to date...")
        enable_extensions()
        create_tables()
        print("✅ Database schema ready")
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Seed users
            print("\n👥 Seeding demo users...")
            users = seed_users(db)
            
            # Seed patients
            print("\n🏥 Seeding demo patients...")
            patients = seed_patients(db, users)
            
            # Seed documents
            print("\n📄 Seeding demo documents...")
            documents = seed_documents(db, users, patients)
            
            print("\n" + "=" * 50)
            print("🎉 Seeding completed successfully!")
            print(f"   Users created/verified: {len(users)}")
            print(f"   Patients created/verified: {len(patients)}")
            print(f"   Documents created/verified: {len(documents)}")
            print("\n🔐 Demo Login Credentials:")
            print("   Doctor:  dr_smith / secure_password")
            print("   Nurse:   nurse_johnson / secure_password") 
            print("   Admin:   admin_wilson / secure_password")
            print("\n🌐 Access the application at: http://localhost:3000")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Seeding failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()