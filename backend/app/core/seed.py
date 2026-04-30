from app.core.database import SessionLocal

from app.models.business_hours import BusinessHours
from datetime import time

def seed_business_hours():
    db = SessionLocal()
    existing = db.query(BusinessHours).first()
    if existing:
        print("Business hours ya existen, omitiendo")
        db.close()
        return
    hours =[
        BusinessHours(day_of_week=0, open_time=None, close_time=None, is_open=False),
        BusinessHours(day_of_week=1, open_time=time(10,0), close_time=time(18,0), is_open=True),
        BusinessHours(day_of_week=2, open_time=time(10,0), close_time=time(18,0), is_open=True),
        BusinessHours(day_of_week=3, open_time=time(10,0), close_time=time(18,0), is_open=True),
        BusinessHours(day_of_week=4, open_time=time(10,0), close_time=time(18,0), is_open=True),
        BusinessHours(day_of_week=5, open_time=time(10,0), close_time=time(18,0), is_open=True),
        BusinessHours(day_of_week=6, open_time=time(10,0), close_time=time(18,0), is_open=True),
    ]

    db.add_all(hours)
    db.commit()
    db.close()
    print("Business hours created")

if __name__ == "__main__":
    seed_business_hours()