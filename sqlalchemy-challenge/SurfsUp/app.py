# Import the dependencies.

import sqlalchemy
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)




# reflect the tables

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################



@app.route("/")
def home():
    """List all available api routes."""
    return (f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>")


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    #calculate date from a year ago 
    date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    past_year = dt.datetime.strptime(date, '%Y-%m-%d') - dt.timedelta(days=365)

    #query prcp for the last 12 months
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= past_year).all()
    
    #convirt tuples into list
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def stations():
    """Return the list of stations"""

    #query list of stations
    results = session.query(station.station).all()  

    #convert tuples into list
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return the tobs for the last year"""
    
    #calculate date one year ago
    date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    past_year = dt.datetime.strptime(date, '%Y-%m-%d') - dt.timedelta(days=365)

    #query most active station
    results = session.query(measurement.station, func.count(measurement.tobs)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.tobs).desc()).\
    first()

    most_active = results[0]

    #query temperature data

    tobs_results = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == most_active).\
    filter(measurement.date >= past_year).all()

    #convert tuples into list
    temps = {date: tobs for date, tobs in tobs_results}

    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start_route(start):
    """Return the TMIN, TAVG, TMAX for greater than or equal to selected date"""

    #query min, max, average from inputed start date
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()

    min_temp, avg_temp, max_temp = results[0]
    
    #convert tuples into list
    temps = {
        'min_temp': min_temp,
        'avg_temp': avg_temp,
        'max_temp': max_temp
    }
    
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):  
    """Return the TMIN, TAVG, TMAX for selected range"""
    
    #query min, max, average from inputed start and end date
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).\
        filter(measurement.date <= end_date).all()

    min_temp, avg_temp, max_temp = results[0]
    
    #convert tuples into list
    temps = {
        'min_temp': min_temp,
        'avg_temp': avg_temp,
        'max_temp': max_temp
    }
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)