import argparse
from sqlalchemy import select
from db_session import Base, engine, SessionLocal
from models_entities import User, UserRole, UserStatus
from core_security import hash_password

parser = argparse.ArgumentParser()
parser.add_argument("--name", required=True)
parser.add_argument("--email", required=True)
parser.add_argument("--password", required=True)
args = parser.parse_args()

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    email = args.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise SystemExit("This email already exists")
    admin = User(full_name=args.name, email=email, password_hash=hash_password(args.password),
                 role=UserRole.ADMIN, status=UserStatus.ACTIVE, preferred_language="ps")
    db.add(admin)
    db.commit()
    print("Administrator created:", email)
finally:
    db.close()
