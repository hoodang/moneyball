import time
from datetime import date, datetime, timedelta
import os
from flask import Flask, flash, redirect, render_template, request, session, abort
import jsonify


from apscheduler.schedulers.background import BackgroundScheduler
import soup.mlb as mlb
import soup.team_rankings as trank
import utils.utes as utes
import utils.emailservice as emailservice
import atexit

app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_LINEUPS_DIR = os.path.join(ROOT_DIR, 'odds_lineups_output')
MLB_LINEUPS_DIR = os.path.join(ROOT_DIR, 'mlb_lineups_output')

@app.route('/')
def hello_world():
    return 'Hello Ballas!'


@app.route('/getLineups/<date>', methods=["GET"])
def get_lineups(date):
    utes.load_properties(filepath=os.path.join(ROOT_DIR, 'moneyball.properties'))
    mlb.load_lineups(date)
    path = os.path.join(MLB_LINEUPS_DIR, date + '_lineups.csv')
    emailservice.send_mail(os.environ.get('gmail_from'), ['lancecreath@gmail.com'],
                           'Lineups Only ' + str(datetime.now()),
                           'Lets make some money - Sent from my Yacht', path)
    return 'Lineups sent!'


@app.route('/sendit', methods=["GET"])
def send_notification():
    # trank.get_historic_odds()
    utes.load_properties(filepath=os.path.join(ROOT_DIR, 'moneyball.properties'))
    target_dt = mlb.todayStr()
    mlb.final_output(target_dt)
    path = os.path.join(OUTPUT_LINEUPS_DIR, target_dt + '_odds_lineups.csv')
    emailservice.send_mail(os.environ.get('gmail_from'), ['lancecreath@gmail.com'],
                           'Odds Lineups ' + str(datetime.now()),
                           'Lets make some money - Sent from my Yacht', path)
    return 'Odds Lineups Sent!'

# sched = BackgroundScheduler(daemon=True)
# sched.add_job(send_notification, 'interval', minutes=45, start_date='2018-07-18 19:51:00',
#                                                            end_date='2018-07-18 21:35:00')
#
# # # Explicitly kick off the background thread
# sched.start()
#
# # job = sched.add_cron_job(my_job, minute="*/15", args=['text'])
#
# #@app.route('/getOddsLineups/<target_dt>', methods=["GET"])
#
#
# # Shutdown your cron thread if the web process is stopped
# atexit.register(lambda: sched.shutdown(wait=False))


def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response


app.after_request(add_cors_headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    # while True:
    #     time.sleep(30)
