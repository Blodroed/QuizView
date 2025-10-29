import gspread
import os
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template

# --- ENVIRONMENT LOAD ---
load_dotenv()

# --- Configuration ---
# Name of your Google Sheet file
SHEET_NAME = str(os.getenv("SHEET_NAME"))
# Name of the specific worksheet (tab)
WORKSHEET_NAME = str(os.getenv("WORKSHEET_NAME"))
# Path to your downloaded service account JSON file
KEYFILE_PATH = str(os.getenv("KEYFILE_PATH"))

# --- App Setup ---
app = Flask(__name__)

# --- Connect to Google Sheets ---
# This is done once when the app starts
try:
    # Authenticate using the service account keyfile
    gc = gspread.service_account(filename=KEYFILE_PATH)
    
    # Open the Google Sheet by its name
    sh = gc.open(SHEET_NAME)
    
    # Select the specific worksheet (tab) by its name
    worksheet = sh.worksheet(WORKSHEET_NAME)
    
    print(f"✅ Successfully connected to '{SHEET_NAME}' - '{WORKSHEET_NAME}'")

except Exception as e:
    print(f"❌ ERROR: Could not connect to Google Sheets: {e}")
    # If connection fails, we set worksheet to None so our routes fail gracefully
    worksheet = None

# --- helper to read the specific ranges H2:H45, I2:I45, J2:J45 ---
def get_scores_from_sheet():
    """
    Returns a list of dicts: [{'rank': '1', 'team': 'Team A', 'points': '100'}, ...]
    Reads H2:H45 (rank), I2:I45 (team), J2:J45 (points).
    """
    if worksheet is None:
        return None

    try:
        ranges = worksheet.batch_get(['H2:H45', 'I2:I45', 'J2:J45'])
        # ranges is a list: [rangeH, rangeI, rangeJ]
        def flatten_col(col_range):
            # col_range is list of rows like [['value1'], ['value2'], ...]
            return [row[0] if len(row)>0 else '' for row in col_range]

        ranks = flatten_col(ranges[0]) if len(ranges) > 0 else []
        teams = flatten_col(ranges[1]) if len(ranges) > 1 else []
        points = flatten_col(ranges[2]) if len(ranges) > 2 else []

        length = max(len(ranks), len(teams), len(points))
        result = []
        for i in range(length):
            r = ranks[i] if i < len(ranks) else ''
            t = teams[i] if i < len(teams) else ''
            p = points[i] if i < len(points) else ''
            # normalize empty rows out (optional: skip entirely blank rows)
            if not (r or t or p):
                continue
            # coerce points to int when possible
            try:
                p_val = int(p)
            except Exception:
                p_val = p
            result.append({'rank': r, 'team': t, 'points': p_val})
        
        # Filter out entries without a team name
        result = [entry for entry in result if entry['team'].strip() != '']

        return result

    except Exception as e:
        # bubble up as None so caller can respond with error
        print(f"Error reading score ranges: {e}")
        return None

# --- API Routes ---
@app.route("/")
def index():
    return "Hello! The G-Sheet server is running. Go to /leaderboard or /api/scores to see the data."

@app.route("/api/scores")
def api_scores():
    """
    JSON endpoint returning the rank/team/points list.
    """
    data = get_scores_from_sheet()
    if data is None:
        return jsonify({"error": "Failed to read spreadsheet or no data available"}), 500
    return jsonify(data)

@app.route("/leaderboard")
def leaderboard():
    """
    Public HTML view with a styled leaderboard table. Auto-refreshes every 10 seconds.
    Uses BETA UiA brand colors.
    """
    data = get_scores_from_sheet()
    if data is None:
        return Response("<h3>Error: could not read spreadsheet.</h3>", mimetype="text/html"), 500

    return render_template('leaderboard.html', data=data)

# --- Run the App ---
if __name__ == "__main__":
    # Host='0.0.0.0' makes it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)