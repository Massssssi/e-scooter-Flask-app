# DinoScooter
## The New Portal for Ecological Travel in Leeds

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

DinoScooter is the first Electric Scooter Web App in Leeds, let's discover it together.

## Description

DinoScooter offers to the people in the Leeds area the benefit of Electric Scooter renting.
The intuitive Web page gives the logged user easy access to all the functionality in one page, the system its also provided with a system of feedbacks. If the User encounters any problem with its Scooter or its reserved session, he cans send a message indicating the problem and the scooter/session involved that will be promptly managed by our Staff.
The Staff can also book a session for unregistered users in order to comply people's requests.

### Features

- Register and start enjoying the full functionality of our service
- Book without registration if you are in a hurry by talking with our staff.
- Look at the map of our Scooter distribution centres.
- Manage Active and Future Sessions to extend or terminate the use of the service.


## Installation

In order to run our app some libraries need to be installed.
Easily install all the needed requirements by going into the app folder and type:
```bash
pip install -r requirements.txt
```
The next step is to initialize the database:
```bash
flask db init
flask db migrate -m "Message"
flask db upgrade
```

We also provided the project with a pre-populated database to test it:
```bash
python3 prepopu_db.py
```

For testing purposes an admin account has been provided:
```bash
username: admin@gmail.com
password: Admin2002!
```

Now you are ready to use the app:
```bash
flask run
```

## Support

Find support at software.project.0011@gmail.com

## Authors and acknowledgement

- Abderrahmane Bennabet
- Adam Brown
- Chemseddine Benimoussa
- Hoi Ching So
- Leonardo Dashi
- Ynyr Evans

## License

SEP
**Free Software!**
