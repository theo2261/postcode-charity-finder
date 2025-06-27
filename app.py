from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Replace with your published Google Sheets CSV URL
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2wk_8ZRselyntpPZEfx3x8ZMyH5O5ri4wwRqzNNXkeoFWqMK7lySLldKTkVEB6j7NQw_bmbNrNlR3/pub?output=csv"

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

        for _, row in services.iterrows():
            service_categories = [cat.strip().lower() for cat in row['Categories'].split(",") if cat.strip()]
            served_areas = [area.strip().upper() for area in row['Postcode Areas'].split(",") if area.strip()]

            # Filter logic:
            # Show all if no category selected
            category_match = (not user_need) or (user_need in service_categories)
            
            # Prioritize postcode-specific, then nationwide
            postcode_specific = any(user_postcode.startswith(area) for area in served_areas if area != "NATIONWIDE")
            nationwide = "NATIONWIDE" in served_areas

            if category_match and (postcode_specific or nationwide):
                results.append((postcode_specific, row))

        # Sort so postcode-specific appear first
        results.sort(key=lambda x: not x[0])

        # Strip out the boolean used for sorting, keep only rows
        results = [r[1] for r in results]

    return render_template("index.html", results=results, categories=sorted_categories)

if __name__ == "__main__":
    app.run(debug=True)
