from flask import Flask, request, render_template
import pandas as pd
import os

app = Flask(__name__)

# Load and clean the CSV
try:
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2wk_8ZRselyntpPZEfx3x8ZMyH5O5ri4wwRqzNNXkeoFWqMK7lySLldKTkVEB6j7NQw_bmbNrNlR3/pub?output=csv"
    services = pd.read_csv(sheet_url)
    services.columns = services.columns.str.strip()
    services.fillna("", inplace=True)
except Exception as e:
    services = pd.DataFrame()
    print("Error loading CSV:", e)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    all_categories = set()
    if not services.empty:
        for cats in services['Categories']:
            for cat in cats.split(","):
                cat = cat.strip()
                if cat:
                    all_categories.add(cat)
    sorted_categories = sorted(all_categories)

    if request.method == "POST" and not services.empty:
        user_postcode = request.form.get("postcode", "").upper().strip()
        user_need = request.form.get("need", "").lower().strip()

        for _, row in services.iterrows():
            service_categories = [
                cat.strip().lower()
                for cat in row['Categories'].split(",")
                if cat.strip()
            ]
            served_areas = [
                area.strip().upper()
                for area in row['Postcode Areas'].split(",")
                if area.strip()
            ]

            if user_need in service_categories and any(user_postcode.startswith(area) for area in served_areas):
                results.append({
                    "name": row.get("Service Name", "Unnamed Service"),
                    "categories": service_categories,
                    "website": row.get("Website", ""),
                    "phone": row.get("Phone Number", "Not available"),
                    "membership": row.get("Membership", ""),
                    "notes": row.get("Notes", "")
                })

    return render_template("index.html", results=results, categories=sorted_categories)

# No debug=True for production
if __name__ != "__main__":
    application = app  # For Render or WSGI servers
