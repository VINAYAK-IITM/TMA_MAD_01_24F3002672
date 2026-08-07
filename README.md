# Vivax - Trekking Management Application

A web-based Trekking Management Application developed using Flask, SQLite, SQLAlchemy, Jinja2, HTML, and CSS. The application provides separate functionalities for Admin, Trek Staff, and Trekkers (Users) to efficiently manage trekking activities, bookings, and participant records.

---

## Features

### Admin
- Secure admin login
- Add, edit, and delete treks
- View all treks
- View all registered users
- View all registered staff
- Approve staff registrations
- Blacklist users and staff
- Assign staff to treks
- View all bookings
- Search users, staff, and treks

### Trek Staff
- Staff registration and login
- Admin approval required before access
- View assigned treks
- Update available slots
- Update trek status
- View registered participants

### Trekker (User)
- User registration and login
- View available treks
- Search treks by location and difficulty
- Book open treks
- View booking history
- Edit profile

---


## Technologies Used

- Python
- Flask
- SQLite
- SQLAlchemy
- Jinja2
- HTML
- CSS

---

## Database Models

### User

- ID
- Name
- Email
- Password
- Contact
- Role
- Approved
- Blacklisted

### Trek

- Trek ID
- Trek Name
- Location
- Difficulty
- Duration
- Available Slots
- Status
- Start Date
- End Date
- Assigned Staff

### Booking

- Booking ID
- User ID
- Trek ID
- Booking Date
- Status

---

## Functionalities Implemented

- User Authentication
- Role-Based Access
- Trek Management
- Trek Booking
- Staff Approval
- Trek Assignment
- Booking History
- Trek Search
- Slot Management
- Automatic Trek Closure when Slots Become Zero

---

## Default Admin Credentials

Email

```
admin@trek.com
```

Password

```
admin123
```

---

## How to Run the Project

1. Install the required packages.

```
pip install flask flask_sqlalchemy
```

2. Navigate to the project folder.

```
cd Vivax
```

3. Run the application.

```
python app.py
```

4. Open your browser and visit

```
http://127.0.0.1:5000
```

---

## Notes

- The database is created automatically using SQLAlchemy.
- Only approved staff members can access the staff dashboard.
- Users can book only treks with Open status.
- Overbooking is prevented by checking available slots.
- When all slots are booked, the trek status is automatically changed to Closed.

---

## Developed By

Vinayak Vashishtha
24F3002672
B.S. Degree Student
DATA SCIENCE AND APPLICATIONS
IIT-MADRAS



