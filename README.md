# moneyball

Deploy to Lambda as Flask app using Zappa: 
  Tutorial: https://hackernoon.com/creating-a-serverless-uptime-monitor-getting-alerted-by-sms-lambda-zappa-python-flask-15c5fb31027
    
  Troubleshooting: When deploying using Zappa, there is an encoding issue in the Zappa program header. In the venv->site-packages->zappa->cli.py file, replace the header with text around ~line 1500. 
  https://github.com/Miserlou/Zappa/issues/825 (Totalus's answer). 
