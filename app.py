from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Load and clean the CSV
services = pd.read_csv("services.csv")
services.columns = services.columns.str.strip()  # Remove extra spaces in headers
services.fillna("", inplace=True)  # Replace NaN with empty strings

@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    # Extract unique, clean category names for the dropdown
    all_categories = set()
    for cats in services['Categories']:
        for cat in cats.split(","):
            cat = cat.strip()
            if cat:
                all_categories.add(cat)
    sorted_categories = sorted(all_categories)

    if request.method == "POST":
        # Get user input
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
                results.append(row)

    return render_template("index.html", results=results, categories=sorted_categories)

if __name__ == "__main__":
    app.run(debug=True)
