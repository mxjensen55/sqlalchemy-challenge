# 1. import Dependencies
  
import numpy as np
from datetime import datetime
import datetime as dt 
import pandas as pd     

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the tables
Measurement = Base.classes.measurement
Station=Base.classes.station
session=Session(engine)
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def welcome():
    return (
        f"Welcome to My Climate App!<br/>"
        f"Below are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"Enter the start date in 'YYYY-MM-DD' format<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Enter the dates in 'YYYY-MM-DD'/'YYYY-MM-DD' format"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    results = session.query(Measurement.date, Measurement.prcp).all()

    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"]=date
        precipitation_dict["prcp"]=prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    query=session.query(Station.name).all()

    all_stations = list(np.ravel(query))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    query=session.query(Measurement.tobs, Measurement.date).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >='2016-08-23').\
        all()

    active_tobs=[]
    for tobs, date in query:
        tobs_dict={}
        tobs_dict["Temperature Observed"]=tobs
        tobs_dict["Date"]=date
        active_tobs.append(tobs_dict)
    print(active_tobs)

    return jsonify(active_tobs)

@app.route("/api/v1.0/<start>")
def trip_start(start):


    start_date= datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime(2017,8, 23)
    trip_data = (session.query(func.min(Measurement.tobs).label('TMin'), func.max(Measurement.tobs).label('TMax'), func.avg(Measurement.tobs).label('TAvg'))
                .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date)
                .filter(func.strftime("%Y-%m-%d", Measurement.date) <= end_date)
                .all())

    start_stats=[]
    for TMin, TMax, TAvg in trip_data:
        temp_dict={}
        temp_dict["Minimum Temp"]=TMin
        temp_dict["Maximum Temp"]=TMax
        temp_dict["Average Temp"]=TAvg
        start_stats.append(temp_dict)
        
    # trip = start_stats(np.ravel(trip_data))
    return jsonify(start_stats)

@app.route("/api/v1.0/<start>/<end>")
def calc_stats(start, end):

    start_date= datetime.strptime(start, '%Y-%m-%d')
    end_date =  datetime.strptime(end, '%Y-%m-%d')

    trip_data = (session.query(func.min(Measurement.tobs).label('TMin'), func.max(Measurement.tobs).label('TMax'), func.avg(Measurement.tobs).label('TAvg'))
                    .filter(Measurement.date >= start_date)
                    .filter(Measurement.date <= end_date)
                    .all())

    begin_end_stats = []
    
    for Tmin, Tmax, Tavg in trip_data:
        begin_end_stats_dict = {}
        begin_end_stats_dict["Minimum Temp"] = Tmin
        begin_end_stats_dict["Maximum Temp"] = Tmax
        begin_end_stats_dict["Average Temp"] = Tavg
        begin_end_stats.append(begin_end_stats_dict)
    
    return jsonify(begin_end_stats)

if __name__ == "__main__":
    app.run(debug=True)