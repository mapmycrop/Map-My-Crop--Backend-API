import schedule
from datetime import datetime
import pytz
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "code"))
from db import SessionLocal
from models import Statistic, User, Farm, Scouting


def statistic_table_update():
    db = SessionLocal()

    statistic = db.query(Statistic).first()

    farmers_count = db.query(User).filter(User.role == 1).count()
    total_farms_mapped = db.query(Farm).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    non_active_users = db.query(User).filter(User.is_active == False).count()
    scouting_total = db.query(Scouting).count()
    paying_farmers = db.query(User).filter(User.is_paid == True).count()
    non_paying_farmers = db.query(User).filter(User.is_paid == False).count()

    if not statistic:

        statistic = Statistic(farmers_count=farmers_count, active_users=active_users, non_active_users=non_active_users, paying_farmers=paying_farmers,
                              non_paying_farmers=non_paying_farmers, total_farms_mapped=total_farms_mapped, scouting_total=scouting_total)

        db.add(statistic)
    else:
        statistic.farmers_count = farmers_count
        statistic.total_farms_mapped = total_farms_mapped
        statistic.active_users = active_users
        statistic.non_active_users = non_active_users
        statistic.scouting_total = scouting_total
        statistic.paying_farmers = paying_farmers
        statistic.non_paying_farmers = non_paying_farmers

    db.commit()

    print("Statistic table is updated.")


IST = pytz.timezone('Asia/Kolkata')

ist_dt = datetime.now(IST)
des_dt = datetime.today().replace(hour=22, minute=0, second=0, tzinfo=IST)

sch_dt = datetime.today().now() + (des_dt - ist_dt)

schedule.every().day.at(sch_dt.strftime("%H:%M:%S")).do(statistic_table_update)

while True:
    schedule.run_pending()
