from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Load and clean the Google Sheet
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2wk_8ZRselyntpPZEfx3x8ZMyH5O5ri4wwRqzNNXkeoFWqMK7lySLldKTkVEB6j7NQw_bmbNrNlR3/pub?output=csv"
services = pd.read_csv(sheet_url)
services.columns = services.columns.str.strip()
services.fillna("", inplace=True)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    # Build dropdown list
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

        local_matches = []
        nationwide_matches = []

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

            postcode_match = (
                "NATIONWIDE" in served_areas or 
                any(user_postcode.startswith(area) for area in served_areas)
            )

            category_match = (
                user_need == "" or user_need in service_categories
            )

            if postcode_match and category_match:
                result = {
                    "name": row.get("Service Name", "Unnamed Service"),
                    "categories": ", ".join(service_categories),
                    "website": row.get("Website", "Not available"),
                    "phone": row.get("Phone", "Not available"),
                    "is_nationwide": "NATIONWIDE" in served_areas
                }

                if result["is_nationwide"]:
                    nationwide_matches.append(result)
                else:
                    local_matches.append(result)

        results = local_matches + nationwide_matches

    return render_template("index.html", results=results, categories=sorted_categories)

if __name__ == "__main__":
    app.run(debug=True)

