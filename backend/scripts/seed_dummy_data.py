"""
Seed script to add dummy users and sample data to MediViewAI.
Run this script from the backend directory:
    python scripts/seed_dummy_data.py
"""
import sys
import os
sys.path.append(os.getcwd())

from app.db.session import get_session
from app.db.models import User, Study, Report, Finding
from app.core.security import get_password_hash
from datetime import datetime


# Dummy users to create
DUMMY_USERS = [
    {
        "email": "admin@mediview.ai",
        "password": "Admin123!",
        "full_name": "Admin User",
        "is_superuser": True
    },
    {
        "email": "doctor@mediview.ai",
        "password": "Doctor123!",
        "full_name": "Dr. Sarah Johnson",
        "is_superuser": False
    },
    {
        "email": "radiologist@mediview.ai",
        "password": "Radio123!",
        "full_name": "Dr. Michael Chen",
        "is_superuser": False
    },
    {
        "email": "nurse@mediview.ai",
        "password": "Nurse123!",
        "full_name": "Emily Davis",
        "is_superuser": False
    },
    {
        "email": "demo@mediview.ai",
        "password": "Demo123!",
        "full_name": "Demo Account",
        "is_superuser": False
    }
]


def create_user(db, user_data):
    """Create a single user if they don't exist."""
    existing = db.query(User).filter(User.email == user_data["email"]).first()
    if existing:
        print(f"  ⏭️  User {user_data['email']} already exists, skipping...")
        return existing
    
    user = User(
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        full_name=user_data["full_name"],
        is_active=True,
        is_superuser=user_data.get("is_superuser", False)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"  ✅ Created user: {user_data['email']}")
    return user


def create_sample_studies(db):
    """Create sample study data."""
    sample_studies = [
        {
            "patient_id": "PAT001",
            "modality": "CT",
            "image_s3_key": "studies/sample/chest_ct_001.dcm",
            "source": "demo",
            "patient_context": "65-year-old male with persistent cough and shortness of breath."
        },
        {
            "patient_id": "PAT002",
            "modality": "MRI",
            "image_s3_key": "studies/sample/brain_mri_001.dcm",
            "source": "demo",
            "patient_context": "42-year-old female presenting with recurring headaches."
        },
        {
            "patient_id": "PAT003",
            "modality": "X-Ray",
            "image_s3_key": "studies/sample/chest_xray_001.dcm",
            "source": "demo",
            "patient_context": "28-year-old male, routine chest examination."
        }
    ]
    
    created_studies = []
    for study_data in sample_studies:
        # Check if study with same s3_key exists
        existing = db.query(Study).filter(Study.image_s3_key == study_data["image_s3_key"]).first()
        if existing:
            print(f"  ⏭️  Study for {study_data['patient_id']} already exists, skipping...")
            created_studies.append(existing)
            continue
        
        study = Study(
            patient_id=study_data["patient_id"],
            modality=study_data["modality"],
            image_s3_key=study_data["image_s3_key"],
            source=study_data["source"],
            patient_context=study_data["patient_context"],
            created_at=datetime.now()
        )
        db.add(study)
        db.commit()
        db.refresh(study)
        created_studies.append(study)
        print(f"  ✅ Created study: {study_data['patient_id']} ({study_data['modality']})")
    
    return created_studies


def create_sample_reports(db, studies):
    """Create sample reports for studies."""
    reports_data = [
        "FINDINGS: The lungs are clear. Heart size is normal. No pleural effusion. "
        "IMPRESSION: Normal chest examination with no acute abnormalities.",
        
        "FINDINGS: Brain parenchyma appears normal. No evidence of mass lesion or hemorrhage. "
        "Ventricles are normal in size. IMPRESSION: Normal brain MRI study.",
        
        "FINDINGS: Cardiopulmonary structures appear within normal limits. "
        "IMPRESSION: No acute cardiopulmonary disease."
    ]
    
    for i, study in enumerate(studies):
        if i >= len(reports_data):
            break
        
        # Check if report exists for this study
        existing = db.query(Report).filter(Report.study_id == study.id).first()
        if existing:
            print(f"  ⏭️  Report for study {study.id} already exists, skipping...")
            continue
        
        report = Report(
            study_id=study.id,
            text=reports_data[i],
            summary_model="gemini-1.5-flash-demo"
        )
        db.add(report)
        db.commit()
        print(f"  ✅ Created report for study {study.id}")


def seed_database():
    """Main function to seed the database with dummy data."""
    print("\n🌱 Seeding MediViewAI database with dummy data...\n")
    
    db = get_session()
    try:
        # Create users
        print("👤 Creating dummy users:")
        for user_data in DUMMY_USERS:
            create_user(db, user_data)
        
        # Create sample studies
        print("\n📋 Creating sample studies:")
        studies = create_sample_studies(db)
        
        # Create sample reports
        print("\n📝 Creating sample reports:")
        create_sample_reports(db, studies)
        
        print("\n" + "=" * 50)
        print("✅ Database seeding completed successfully!")
        print("=" * 50)
        
        print("\n🔐 LOGIN CREDENTIALS:")
        print("-" * 50)
        for user in DUMMY_USERS:
            role = "Admin" if user["is_superuser"] else "User"
            print(f"  Email:    {user['email']}")
            print(f"  Password: {user['password']}")
            print(f"  Name:     {user['full_name']} ({role})")
            print("-" * 50)
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
