from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user
import pandas as pd
import io

from moodle_sync_testing import MoodleSyncTesting

from models import logger

gridjs = Blueprint("gridjs", __name__, url_prefix="/gridjs")

@gridjs.route("/")
def gridjs_get():
    return render_template("gridjs.html")

@gridjs.route("/2")
def gridjs2_get():
    df = pd.read_csv("data/test.csv")
    df = df.to_json(orient="records")
    print(df)
    return df
