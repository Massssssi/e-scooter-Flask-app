from app import db, models
from werkzeug.security import generate_password_hash, check_password_hash

#Creates the admin account(Manger):
p = models.User(forename = "admin", surname = "Admin", email= "admin@gmail.com", password = generate_password_hash("Admin2002!", method='sha256'), phone = "+447494212033", account_type =2, national_insurance_number = "ppppppppp", discount = False)
db.session.add(p)

#Creates the 5 locations:
p = models.Location(address = "Trinity centre", no_of_scooters = 0)
db.session.add(p)
p = models.Location(address = "Train station", no_of_scooters = 0)
db.session.add(p)
p = models.Location(address = "Merrion centre", no_of_scooters = 0)
db.session.add(p)
p = models.Location(address = "LGI hospital", no_of_scooters = 0)
db.session.add(p)
p = models.Location(address = "UoL Edge sports centre", no_of_scooters = 0)
db.session.add(p)

#Creates the hourly cost:
p = models.ScooterCost(hourly_cost = 10)
db.session.add(p)

#Adding sccoters:
for j in range(5):
    l = models.Location.query.filter_by(id = j+1).first()
    for i in range(0, 5):
            scooter = models.Scooter(availability=True, location_id=j+1)
            db.session.add(scooter)
            l.no_of_scooters += 1

db.session.commit()
