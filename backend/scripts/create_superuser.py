import sys
import os
sys.path.append(os.getcwd())

from app.db.session import get_session
from app.db.models import User
from app.core.security import get_password_hash

def create_superuser(email, password, full_name):
    # db = SessionLocal() -> This was None
    db = get_session()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User {email} already exists")
            return
        
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=True
        )
        db.add(user)
        db.commit()
        print(f"Superuser {email} created successfully")
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser("admin@mediview.ai", "admin123", "Admin User")
