# BETA Quiz Leaderboard

A simple leaderboard which pulls data from a google sheet and then displays it on a live updating leaderboard.

## Configuration

1. Copy the excel sheet found in the teams or given by the quiz staff and paste it as a google sheet where you know it will stay. Really important that it is a google sheet not excel for this to work.
2. Then open the google cloud console and register and app to get an API key for the google sheets API.
3. Get your json credentials for the google sheets API and place it in the root directory of the project as `key.json`.
4. Copy the .env.example file to .env and fill in the required fields.

*A detailed guide on google sheets API can be found [Google Cloud Docs](https://docs.cloud.google.com/iam/docs/service-accounts-create).*

## Running the App

1. Make sure you have python installed on your machine.
2. Install `uv` package manager if you do not have it already.
3. Create a venv with `uv venv` and activate it.
4. Install the requirements with `uv sync`.
5. Run the app with `uv run main.py`.
