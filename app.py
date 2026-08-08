from flask import Flask, render_template, request, redirect, session
from models import db, User, Trek, Booking
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "trekkingproject"

db.init_app(app)

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(role="admin").first()

    if admin is None:
        admin = User(
            name="Administrator",
            email="admin@trek.com",
            password="admin123",
            contact="9999999999",
            role="admin",
            approved=True,
            blacklisted=False
        )

        db.session.add(admin)

    else:
        admin.email = "admin@trek.com"
        admin.password = "admin123"
        admin.approved = True
        admin.blacklisted = False

    db.session.commit()


def admin_logged_in():
    return session.get("role") == "admin"


def staff_logged_in():
    return session.get("role") == "staff"


def user_logged_in():
    return session.get("role") == "user"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user is None:
            return render_template(
                "login.html",
                message="User does not exist."
            )

        if user.password != password:
            return render_template(
                "login.html",
                message="Incorrect password."
            )

        if user.blacklisted:
            return render_template(
                "login.html",
                message="Your account has been blacklisted."
            )

        if user.role == "staff" and not user.approved:
            return render_template(
                "login.html",
                message="Waiting for Admin Approval."
            )

        session["user_id"] = user.id
        session["role"] = user.role

        if user.role == "admin":
            return redirect("/admin/dashboard")

        if user.role == "staff":
            return redirect("/staff/dashboard")

        return redirect("/user/dashboard")

    return render_template("login.html")

@app.route("/admin/add-trek", methods=["GET", "POST"])
def add_trek():

    if not admin_logged_in():
        return redirect("/login")

    if request.method == "POST":

        trek = Trek(

            trek_name=request.form["trek_name"],

            location=request.form["location"],

            difficulty=request.form["difficulty"],

            duration=int(request.form["duration"]),

            available_slots=int(request.form["available_slots"]),

            status=request.form["status"],

            start_date=datetime.strptime(
                request.form["start_date"],
                "%Y-%m-%d"
            ).date(),

            end_date=datetime.strptime(
                request.form["end_date"],
                "%Y-%m-%d"
            ).date()

        )

        db.session.add(trek)

        db.session.commit()

        return redirect("/admin/dashboard")

    return render_template("admin_add_trek.html")



@app.route("/admin/treks")
def view_treks():

    if not admin_logged_in():
        return redirect("/login")

    treks = Trek.query.order_by(Trek.id).all()

    return render_template(
        "admin_treks.html",
        treks=treks
    )



@app.route("/admin/edit-trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):

    if not admin_logged_in():
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":

        trek.trek_name = request.form["trek_name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = int(request.form["duration"])
        trek.available_slots = int(request.form["available_slots"])
        trek.status = request.form["status"]

        trek.start_date = datetime.strptime(
            request.form["start_date"],
            "%Y-%m-%d"
        ).date()

        trek.end_date = datetime.strptime(
            request.form["end_date"],
            "%Y-%m-%d"
        ).date()

        db.session.commit()

        return redirect("/admin/treks")

    return render_template(
        "admin_edit_trek.html",
        trek=trek
    )



@app.route("/admin/delete-trek/<int:trek_id>")
def delete_trek(trek_id):

    if not admin_logged_in():
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)

    db.session.commit()

    return redirect("/admin/treks")




@app.route("/admin/staff")
def admin_staff():

    if not admin_logged_in():
        return redirect("/login")

    staffs = User.query.filter_by(role="staff").order_by(User.id).all()

    return render_template(
        "admin_staff.html",
        staffs=staffs
    )




@app.route("/admin/approve-staff/<int:staff_id>")
def approve_staff(staff_id):

    if not admin_logged_in():
        return redirect("/login")

    staff = User.query.get_or_404(staff_id)

    staff.approved = True

    db.session.commit()

    return redirect("/admin/staff")




@app.route("/admin/blacklist-staff/<int:staff_id>")
def blacklist_staff(staff_id):

    if not admin_logged_in():
        return redirect("/login")

    staff = User.query.get_or_404(staff_id)

    staff.blacklisted = True

    db.session.commit()

    return redirect("/admin/staff")



@app.route("/admin/assign-trek/<int:staff_id>", methods=["GET", "POST"])
def assign_trek(staff_id):

    if not admin_logged_in():
        return redirect("/login")

    staff = User.query.get_or_404(staff_id)

    if request.method == "POST":

        trek = Trek.query.get(request.form["trek_id"])

        if trek is None:
            return redirect("/admin/staff")

        trek.staff_id = staff.id

        db.session.commit()

        return redirect("/admin/staff")

    treks = Trek.query.order_by(Trek.trek_name).all()

    return render_template(
        "admin_assign_trek.html",
        staff=staff,
        treks=treks
    )



@app.route("/admin/search", methods=["GET", "POST"])
def admin_search():

    if not admin_logged_in():
        return redirect("/login")

    results = []

    category = ""

    if request.method == "POST":

        category = request.form["category"]

        keyword = request.form["keyword"]

        if category == "users":

            results = User.query.filter(
                User.role == "user",
                User.name.contains(keyword)
            ).all()

        elif category == "staff":

            results = User.query.filter(
                User.role == "staff",
                User.name.contains(keyword)
            ).all()

        else:

            results = Trek.query.filter(
                Trek.trek_name.contains(keyword)
            ).all()

    return render_template(
        "admin_search.html",
        results=results,
        category=category
    )



@app.route("/admin/users")
def admin_users():

    if not admin_logged_in():
        return redirect("/login")

    users = User.query.filter_by(role="user").order_by(User.id).all()

    return render_template(
        "admin_users.html",
        users=users
    )



@app.route("/admin/blacklist-user/<int:user_id>")
def blacklist_user(user_id):

    if not admin_logged_in():
        return redirect("/login")

    user = User.query.get_or_404(user_id)

    user.blacklisted = True

    db.session.commit()

    return redirect("/admin/users")



@app.route("/admin/bookings")
def admin_bookings():

    if not admin_logged_in():
        return redirect("/login")

    bookings = Booking.query.order_by(Booking.id).all()

    return render_template(
        "admin_bookings.html",
        bookings=bookings
    )




@app.route("/admin/history")
def admin_history():

    if not admin_logged_in():
        return redirect("/login")

    completed_treks = Trek.query.filter_by(
        status="Completed"
    ).all()

    completed_bookings = Booking.query.filter_by(
        status="Completed"
    ).all()

    return render_template(
        "admin_history.html",
        treks=completed_treks,
        bookings=completed_bookings
    )




@app.route("/register/user", methods=["GET", "POST"])
def register_user():

    if request.method == "POST":

        email = request.form["email"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template(
                "register_user.html",
                message="Email already registered."
            )

        user = User(
            name=request.form["name"],
            email=email,
            password=request.form["password"],
            contact=request.form["contact"],
            role="user",
            approved=True,
            blacklisted=False
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register_user.html")


@app.route("/register/staff", methods=["GET", "POST"])
def register_staff():

    if request.method == "POST":

        email = request.form["email"]

        existing_staff = User.query.filter_by(email=email).first()

        if existing_staff:
            return render_template(
                "register_staff.html",
                message="Email already registered."
            )

        staff = User(
            name=request.form["name"],
            email=email,
            password=request.form["password"],
            contact=request.form["contact"],
            role="staff",
            approved=False,
            blacklisted=False
        )

        db.session.add(staff)
        db.session.commit()

        return redirect("/login")

    return render_template("register_staff.html")




@app.route("/staff/dashboard")
def staff_dashboard():

    if not staff_logged_in():
        return redirect("/login")

    treks = Trek.query.filter_by(
        staff_id=session["user_id"]
    ).all()

    return render_template(
        "staff_dashboard.html",
        treks=treks
    )




@app.route("/staff/manage-trek/<int:trek_id>", methods=["GET", "POST"])
def manage_trek(trek_id):

    if not staff_logged_in():
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != session["user_id"]:
        return redirect("/staff/dashboard")

    if request.method == "POST":

        trek.available_slots = int(
            request.form["available_slots"]
        )

        trek.status = request.form["status"]
        if trek.status == "Completed":

            bookings = Booking.query.filter_by(trek_id=trek.id).all()

            for booking in bookings:
                booking.status = "Completed"
        
        db.session.commit()

        return redirect("/staff/dashboard")

    return render_template(
        "staff_manage_trek.html",
        trek=trek
    )



@app.route("/user/dashboard")
def user_dashboard():

    if not user_logged_in():
        return redirect("/login")

    user = User.query.get(session["user_id"])

    return render_template(
        "user_dashboard.html",
        user=user
    )



@app.route("/user/treks")
def user_treks():

    if not user_logged_in():
        return redirect("/login")

    query = Trek.query.filter_by(status="Open")

    location = request.args.get("location")

    difficulty = request.args.get("difficulty")

    if location:
        query = query.filter(Trek.location.contains(location))

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    treks = query.all()

    return render_template(
        "user_treks.html",
        treks=treks
    )




@app.route("/user/bookings")
def user_bookings():

    if not user_logged_in():
        return redirect("/login")

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "user_bookings.html",
        bookings=bookings
    )




@app.route("/user/profile", methods=["GET", "POST"])
def user_profile():

    if not user_logged_in():
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        email = request.form["email"]

        existing_user = User.query.filter(
            User.email == email,
            User.id != user.id
        ).first()

        if existing_user:

            return render_template(
                "user_profile.html",
                user=user,
                message="Email already exists."
            )

        user.name = request.form["name"]

        user.email = email

        user.contact = request.form["contact"]

        user.password = request.form["password"]

        db.session.commit()

        return render_template(
            "user_profile.html",
            user=user,
            message="Profile updated successfully."
        )

    return render_template(
        "user_profile.html",
        user=user
    )



@app.route("/user/book/<int:trek_id>")
def book_trek(trek_id):

    if not user_logged_in():
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id is None:
        return render_template(
            "booking_error.html",
            message="No staff has been assigned to this trek yet."
        )

    if trek.status != "Open":
        return render_template(
            "booking_error.html",
            message="This trek is not open for booking."
        )

    if trek.available_slots <= 0:
        return render_template(
            "booking_error.html",
            message="No slots available."
        )

    existing_booking = Booking.query.filter_by(
        user_id=session["user_id"],
        trek_id=trek.id
    ).first()

    if existing_booking:
        return render_template(
            "booking_error.html",
            message="You have already booked this trek."
        )

    booking = Booking(
        user_id=session["user_id"],
        trek_id=trek.id,
        booking_date=datetime.today().date(),
        status="Booked"
    )

    db.session.add(booking)

    trek.available_slots -= 1

    if trek.available_slots <= 0:
        trek.available_slots = 0
        trek.status = "Closed"

    db.session.commit()

    return render_template("booking_success.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


@app.route("/admin/dashboard")
def admin_dashboard():

    if not admin_logged_in():
        return redirect("/login")

    total_treks = Trek.query.count()

    total_users = User.query.filter_by(role="user").count()

    total_staff = User.query.filter_by(role="staff").count()

    total_bookings = Booking.query.count()

    return render_template(
        "admin_dashboard.html",
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings
    )


if __name__ == "__main__":
    app.run(debug=True)