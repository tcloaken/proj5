#! /bin/python3

"""
Very simple Flask web site, with one page
displaying a course schedule.

"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify # For AJAX transactions

import json
import logging

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Our own module
import acp_times

###
# Globals
###
app = flask.Flask(__name__)
import CONFIG

app = flask.Flask(__name__)
import CONFIG
app.secret_key = CONFIG.secret_key  # Should allow using session variables

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Main page entry")
  return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("/")
    return flask.render_template('page_not_found.html'), 404


###############
#
# AJAX request handlers 
#   These return JSON, rather than rendering pages. 
#
###############
@app.route("/_calc_times")
def _calc_times():
  """
  Calculates open/close times from miles, using rules 
  described at https://rusa.org/octime_alg.html.
  Expects 4 URL-encoded arguments, the contorl number of km, start time, start date, 
  and total brevet distance. 
  """
  
  app.logger.debug("Got a JSON request");
  km = request.args.get('km', 0, type=int)
  start_time = request.args.get('start_time',"",type=str)
  start_date = request.args.get('start_date',"",type=str)
  dist = request.args.get('dist', 0,type=int)
  start = arrow.get(start_date +" "+ start_time +":00", 'YYYY-MM-DD HH:mm:ss').isoformat()
  app.logger.debug(start)
  open_time = acp_times.open_time(km, dist, start)
  close_time = acp_times.close_time(km, dist, start)
  result={ "open": open_time, "close": close_time }
  return jsonify(result=result)


#############

if __name__ == "__main__":
    # Standalone. 
    app.debug = True
    app.logger.setLevel(logging.DEBUG)
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
else:
    # Running from cgi-bin or from gunicorn WSGI server, 
    # which makes the call to app.run.  Gunicorn may invoke more than
    # one instance for concurrent service.
    #FIXME:  Debug cgi interface 
    app.debug=False
