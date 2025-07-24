from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure random string

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Hardcoded user
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Password constant
PASSWORD = "PinkBananas34"
USERNAME = "admin"

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == PASSWORD:
            user = User(USERNAME)
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Incorrect password. Try again.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Load live data from Google Sheets
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT5VSfWySQ3GK6e9Hi5PurTdmYvJVUssVTEed2k8gma6FpE-JsFzeJDP3e-QrcPVqe2n1jSHS8r0L4C/pub?output=csv"
    services = pd.read_csv(sheet_url)
    services.columns = services.columns.str.strip()
    services.fillna("", inplace=True)

    results = []
    all_categories = set()
    for cats in services['Categories']:
        for cat in cats.split(","):
            cat = cat.strip()
            if cat:
                all_categories.add(cat)
    sorted_categories = sorted(all_categories)

    if request.method == "POST":
        user_postcode = request.form.get("postcode", "").upper().strip()
        user_need = request.form.get("need", "").lower().strip()
        is_leeds_postcode = user_postcode.startswith("LS")

        for _, row in services.iterrows():
            service_categories = [cat.strip().lower() for cat in row['Categories'].split(",") if cat.strip()]
            served_areas = [area.strip().upper() for area in row['Postcode Areas'].split(",") if area.strip()]
            category_match = (not user_need) or (user_need in service_categories)

            service_type = None
            if any(user_postcode.startswith(area) for area in served_areas if area not in ("LEEDSWIDE", "NATIONWIDE")):
                service_type = "Local"
            elif "LEEDSWIDE" in served_areas and is_leeds_postcode:
                service_type = "Leedswide"
            elif "NATIONWIDE" in served_areas:
                service_type = "Nationwide"

            if category_match and service_type:
                results.append((service_type, row))

        type_order = {"Local": 0, "Leedswide": 1, "Nationwide": 2}
        results.sort(key=lambda x: type_order.get(x[0], 3))
        results = [{"type": r[0], "data": r[1]} for r in results]

    return render_template("index.html", results=results, categories=sorted_categories)

if __name__ == "__main__":
    app.run(debug=True)
