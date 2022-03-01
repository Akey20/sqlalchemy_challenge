#for app.py testing in jupyter notebook first.## SQLALCHEMY HOMEWORK APP ##

### 1. import Flask
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

### 2. Create Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
#  tables
Base.prepare(engine, reflect=True)
#  reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

### 3.Setup Flask
app = Flask(__name__)


### Routes
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"AKey20 SQLAchemy Homework assignment number 10 - SURFS UP! </br>"
        f"This is my Climate App that I have created.</br> "
        f"Available Routes:</br>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
        f"<li>/about</li>"
        f"</ul>"
    )


@app.route("/about")
def about():
    print("Server received request for 'About' page...")
    return(
        f"My name is April Key.</br>"
    ) 


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Servier received request for '/api/v1.0/precipitation'.")
    # Create session (link) from Python to the DB
    session = Session(engine) 
    # Query date and prcp then turn into a dictionary
    data_prcp = session.query(Measurement.date, Measurement.prcp)\
        .order_by(Measurement.date.desc()).filter(Measurement.date > '2016-08-23').all()
    
    # Use For Loop to create a dictionary
    prcp_dict = {}
    for date, prcp in data_prcp:
        # First see if the key or date is already there if not add or append
        if date not in prcp_dict:
            prcp_dict[date] = []
            prcp_dict[date].append(prcp)
        # If key with the same date is already there, then use append
        else:
            prcp_dict[date].append(prcp)
 
 # Close session 
    session.close()        

    return jsonify(prcp_dict)

### Create route "/api/v1.0/stations"

@app.route("/api/v1.0/stations")
def stations():
    # Create link to the DB
    session = Session(engine)
    stations_active = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # Create a list of stations ids
    stations_ids = []
    for station_active in stations_active:
        station = station_active[0]
        stations_ids.append(station)
    
    # Return a JSON list from the dataset
    stations = {}
    stations['stations'] = stations_ids
    
    session.close()
    
    return jsonify(stations)

###  Create route "<li>/api/v1.0/tobs</li>"
# Query the dates and temperature observations for the most active station -lowest, highest & avg temp.
# Return a JSON list of (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    stations_active = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # Find most active station
    station_most_active=stations_active[0][0]
    
    # Dine Weather for Most Active Station
    weather = session.query(func.min(Measurement.tobs),\
    func.max(Measurement.tobs),\
    func.avg(Measurement.tobs)).filter(Measurement.station == station_most_active).all()

    # Convert tuple to a list
    weather_list = list(weather[0])
     
    # Return a JSON list 
    station_weather = {}
    station_weather['weather'] = weather_list
    
    session.close()
    
    return jsonify(station_weather)

### Create route "/api/v1.0/<start>"
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def date_starts(start):
    print("Server received request for '/api/v1.0/<start>'.")
     # Create our session (link) from Python to the DB
    session = Session(engine) 
    # Query date and prcp from database and then turn into a dictionary
    # Lowest, avgerage, and highest temperature query
    station_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.station == 'USC00519281')\
        .filter(Measurement.date >= start).first()
 
    session.close()

    # Create dictionary with the results
    temps_dict = {"Low Temp": station_results[0], "Average Temp": station_results[1], "Hi Temp": station_results[2]}

    return jsonify(temps_dict)

###  Create route "/api/v1.0/<start>/<end>"

@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    print("Server received request for '/api/v1.0/<start>/<end>'.")
     # Create our session link
    session = Session(engine) 
    # Query start date, end date, and TOBS data from database and then turn into a dictionary
    station_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.station == 'USC00519281')\
        .filter(Measurement.date <= end)\
        .filter(Measurement.date >= start).first()

    session.close()

    # Create dictionary to output
    temps_dict = {"Low Temp": station_results[0], "Average Temp": station_results[1], "Hi Temp": station_results[2]}

    return jsonify(temps_dict)

if __name__ == '__main__':
    app.run()