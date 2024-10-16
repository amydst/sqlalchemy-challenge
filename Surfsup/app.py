# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_record = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_record[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    year_ago = last_date - dt.timedelta(days=365)
    sel = [Measurement.date,Measurement.prcp]
    precipitation_info = session.query(*sel).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()
    session.close()
    precipitation_dates = []
    for d, p in precipitation_info:
        precipitation_dict = {}
        precipitation_dict["date"] = d
        precipitation_dict["prcp"] = p
        precipitation_dates.append(precipitation_dict)
    
    return(jsonify(precipitation_dates))

@app.route("/api/v1.0/stations")
def stations():
    # Query the database for all station data
    station_list = session.query(Station.station).all()
    
    # Convert the query result to a list of dictionaries
    stations = [{"station": station[0]} for station in station_list]
    
    # Return the JSONified list of stations
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temperature():
    
    most_active = 'USC00519281'
    last_record = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_record[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    year_ago = last_date - dt.timedelta(days=365)
    temperature_query = session.query(
        Measurement.date, Measurement.tobs
        ).filter(Measurement.station == most_active).filter(Measurement.date >= year_ago).all()

    temp_info = []
    for d, t in temperature_query:
        temp_dict = {}
        temp_dict["date"] = d
        temp_dict["tobs"] = t
        temp_info.append(temp_dict)
    
    return(jsonify(temp_info))

@app.route("/api/v1.0/<start>", methods=["GET"])
def query_start(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    temperature_query = session.query(
        Measurement.date,
        func.min(Measurement.tobs).label('min_temp'),
        func.max(Measurement.tobs).label('max_temp'),
        func.avg(Measurement.tobs).label('avg_temp')
        ).filter(Measurement.date >= start_date).group_by(Measurement.date).all()

    session.close()

    temp_info = []
    for d, min, max, avg in temperature_query:
        temp_dict = {}
        temp_dict["date"] = d
        temp_dict["min"] = min
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        temp_info.append(temp_dict)
    
    return(jsonify(temp_info))

@app.route("/api/v1.0/<start>/<end>", methods = ["GET"])
def query_start_end(start,end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    temperature_query = session.query(
        Measurement.date,
        func.min(Measurement.tobs).label('min_temp'),
        func.max(Measurement.tobs).label('max_temp'),
        func.avg(Measurement.tobs).label('avg_temp')
        ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()

    session.close()

    temp_info = []
    for d, min, max, avg in temperature_query:
        temp_dict = {}
        temp_dict["date"] = d
        temp_dict["min"] = min
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        temp_info.append(temp_dict)
    
    return(jsonify(temp_info))


if __name__ == "__main__":
    app.run(debug=True)
