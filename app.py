# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Assign the date exactly one year before the most recent measurement
recent_date = dt.date(2016, 8, 23)

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Check the engine is correct
print(engine.url)

# Print tables
print(Base.classes.keys())

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
    
    # List all possible routes
    return(
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Select date, station name, and precipitation from the most recent year for all stations
    results = (
        session.query(Measurement.date, Station.id, Station.name, Measurement.prcp)
        .filter(Measurement.station == Station.station)
        .filter(Measurement.date >= recent_date)
        .all()
    )

    session.close()

    prcp_list = []
    for date, id, name, prcp in results:
        dict = {}
        dict[date] = prcp
        dict[f"station {id}"] = name
        prcp_list.append(dict)

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():

    # Select all station identifiers and names
    results = session.query(Station.station, Station.name).all()

    session.close()

    station_list = []
    for station, name in results:
        dict = {}
        dict[station] = name
        station_list.append(dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    # Select date and temperature for the most active station in the recent year
    results = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == "USC00519281")
        .filter(Measurement.date >= recent_date)
        .all()
    )

    session.close()

    tobs_list = []
    for date, tobs in results:
        dict = {}
        dict[date] = tobs
        tobs_list.append(dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def date_from(start):

    # Check if input date string can be parsed by datetime
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")

        # List columns to be queried
        sel = [
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ]
        # Query the database
        results = (
            session.query(*sel)
            .filter(Measurement.date >= start_date)
            .all()
        )

        session.close()

        # Create jsonified return
        t_summary = []
        for min, avg, max in results:
            dict = {}
            dict["TMIN"] = min
            dict["TAVG"] = avg
            dict["TMAX"] = max
            t_summary.append(dict)
            
        return jsonify(t_summary)
        
    # If input cannot be parsed, then return error
    except ValueError:
        return jsonify({"error": f"Date input not recognized"}), 404

@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):

    # Check if input date string can be parsed by datetime
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")

        # List the columns to be queried
        sel = [
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)
        ]
        # Query the database
        results = (
            session.query(*sel)
            .filter(Measurement.date >= start_date)
            .filter(Measurement.date <= end_date)
            .all()
        )

        session.close()

        # Create jsonified return
        t_summary = []
        for min, avg, max in results:
            dict = {}
            dict["TMIN"] = min
            dict["TAVG"] = avg
            dict["TMAX"] = max
            t_summary.append(dict)
            
        return jsonify(t_summary)
    
    # If input cannot be parsed, then return error
    except ValueError:
        return jsonify({"error": f"Date input not recognized"}), 404

if __name__ == "__main__":
    app.run(debug=True)