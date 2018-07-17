import time
from datetime import date, datetime, timedelta
import os

from flask import Flask, request


from apscheduler.schedulers.background import BackgroundScheduler
import soup.mlb as mlb
import soup.team_rankings as trank
import utils.utes as utes
import utils.emailservice as emailservice
import atexit

app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_LINEUPS_DIR = os.path.join(ROOT_DIR, 'odds_lineups_output')

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
    path = os.path.join(OUTPUT_LINEUPS_DIR, target_dt + '_odds_lineups.csv')
    emailservice.send_mail(os.environ.get('gmail_from'), ['lancecreath@gmail.com', 'spencer.levy@outlook.com'],
                           'Odds Lineups ' + str(datetime.now()),
                           'Lets make some money - Sent from my Yacht', path)

sched = BackgroundScheduler(daemon=True)
sched.add_job(send_notification, 'interval', minutes=45, start_date='2018-07-14 11:15:00', end_date='2018-07-14 21:35:00')

# # Explicitly kick off the background thread
sched.start()

# job = sched.add_cron_job(my_job, minute="*/15", args=['text'])

#@app.route('/getOddsLineups/<target_dt>', methods=["GET"])


# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: sched.shutdown(wait=False))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=33)
    utes.load_properties(filepath=os.path.join(ROOT_DIR, 'moneyball.properties'))
    while True:
        time.sleep(30)
