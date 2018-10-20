#import dependencies
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

#import sqlalchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

#setup engine and prevents weird error from last api route from popping up
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})

# Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

#set up classes for reference
Measurement = Base.classes.measurement
Station = Base.classes.station

#set up session
session = Session(engine)

#### Flask App

app = Flask(__name__)

#frequently used variable
year_ago = (dt.date(2017,8,23) - dt.timedelta(days=365)).isoformat()

#homepage
@app.route('/')
def homepage():
    return(
        f"Welcome to the Surfs Up API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/*put a date here* <br/>"
        f"/api/v1.0/*put a start date here*/*put an end date here*<br/>"
    )

#Convert the query results to a Dictionary using date as the key and tobs as the value.
#Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation')
def precipitation():
    q_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > year_ago).group_by(Measurement.date).all()
    q_dict = {}
    for result in q_results:
        q_dict[str(result.date)] = result.prcp
    return jsonify(q_dict)

#Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    stations = session.query(Station.station, Station.name).all()
    return jsonify(stations)

#query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
    tempobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    return jsonify(tempobs)

#Return a JSON list of the minimum temperature, the average temperature, 
#and the max temperature for a given start or start-end range.

#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route('/api/v1.0/<start>')
def skeptic(start):
    quitter = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    return jsonify(quitter)

#When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
#for dates between the start and end date inclusive.
@app.route('/api/v1.0/<start>/<end>')
def optomist(start,end):
    finisher = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date<= end).all()
    return jsonify(finisher)

#last line
if __name__ == '__main__':
    app.run(debug=True)