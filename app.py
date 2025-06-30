from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Replace with your published Google Sheets CSV URL
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceA3AJ0IFgBXN4RtiZfradv9Mt0cr81wmGVwWS8bYz13z4Pox_Hr8nC0af_o4_-hSiDEVhxs5J18R/pub?output=csv"

# Load and clean the CSV from Google Sheets
services = pd.read_csv(sheet_url)
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
        user_postcode = request.form.get("postcode", "").upper().strip()
        user_need = request.form.get("need", "").lower().strip()
        is_leeds_postcode = user_postcode.startswith("LS")

        for _, row in services.iterrows():
            service_categories = [cat.strip().lower() for cat in row['Categories'].split(",") if cat.strip()]
            served_areas = [area.strip().upper() for area in row['Postcode Areas'].split(",") if area.strip()]

            category_match = (not user_need) or (user_need in service_categories)

            # Match type
            service_type = None
            if any(user_postcode.startswith(area) for area in served_areas if area not in ("LEEDSWIDE", "NATIONWIDE")):
                service_type = "Local"
            elif "LEEDSWIDE" in served_areas and is_leeds_postcode:
                service_type = "Leedswide"
            elif "NATIONWIDE" in served_areas:
                service_type = "Nationwide"

            if category_match and service_type:
                results.append((service_type, row))

        # Sort order: Local > Leedswide > Nationwide
        type_order = {"Local": 0, "Leedswide": 1, "Nationwide": 2}
        results.sort(key=lambda x: type_order.get(x[0], 3))

        # Format for template
        results = [{"type": r[0], "data": r[1]} for r in results]

    return render_template("index.html", results=results, categories=sorted_categories)

if __name__ == "__main__":
    app.run(debug=True)
