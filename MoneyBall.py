from datetime import date, datetime, timedelta
import this
from time import strftime

from flask import Flask, request
from flask_apscheduler import scheduler as scheduler


from apscheduler.schedulers.background import BackgroundScheduler
import soup.mlb as mlb
import soup.team_rankings as trank
from pathlib import Path
import utils.emailservice as emailservice
import utils.utes as utes
import atexit

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/getLineups/<date>', methods=["GET"])
def get_lineups(date):
    mlb.load_lineups(date)

def send_notification():
    trank.get_historic_odds()
    target_dt = mlb.todayStr()
    mlb.final_output(target_dt)
    path = utes.abPath(mlb.project_base + 'odds_lineups_output/' + target_dt + '_odds_lineups.csv')
    emailservice.send_mail('lancecreath@gmail.com', ['lancecreath@gmail.com', 'spencer.levy@outlook.com'],
                           'Odds Lineups ' + str(datetime.now()),
                           'Lets make some money - Sent from my Yacht', path)

sched = BackgroundScheduler(daemon=True)
sched.add_job(send_notification, 'interval', minutes=30, start_date='2018-06-22 18:30:00', end_date='2018-06-22 21:01:00')
# # Explicitly kick off the background thread
sched.start()

# job = sched.add_cron_job(my_job, minute="*/15", args=['text'])

#@app.route('/getOddsLineups/<target_dt>', methods=["GET"])


# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: sched.shutdown(wait=False))

if __name__ == '__main__':
    app.run(debug=False, host="73.44.65.29", port=33)