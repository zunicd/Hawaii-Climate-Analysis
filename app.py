import numpy as np
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
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to both tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Calculate the date 1 year ago from the last data point in the database
last_date = session.query(Measurement.date).\
            order_by(Measurement.date.desc()).first()
year_ago = dt.datetime.strptime(last_date[0], '%Y-%m-%d')\
            .date() - dt.timedelta(days=365)

# Calculate the first data point in the database
first_date = session.query(Measurement.date).\
            order_by(Measurement.date.asc()).first()

# Save the list of all dates
date_list = np.ravel(session.query(Measurement.date).all())

session.close()

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
        f"/api/v1.0/2016-10-09<br/>"
        f"/api/v1.0/2016-10-09/2016-10-30"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the last 12 months of precipitation data"""

    # Perform a query to retrieve the data and precipitation scores
    prcps = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= year_ago).\
                order_by(Measurement.date).all()
    
    session.close()

    # Remove nulls (NaNs)
    prcps = [pobs for pobs in prcps if not pd.isna(pobs[1])]
    
    # Convert the query results to a dictionary using date as the key and prcp as the value
    all_prcps = []
    for date, prcp in prcps:
        prcp_dict = {}
        prcp_dict[date] = prcp
     
        all_prcps.append(prcp_dict)

    return jsonify(all_prcps)

    

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Query all stations

    stations = session.query(Station.station, Station.name, Station.latitude, 
                func.round(Station.longitude,5), Station.elevation).all()

    session.close()

  # Create list of dictionaries
    all_stations = []

    for station, name, lat, lng, elevation in stations:
        # create two dictionaries
        st_dict = {}
        stinfo_dict = {}
        st_dict['station ID'] = station
        stinfo_dict['name'] = name
        stinfo_dict['latitude'] = lat
        stinfo_dict['longitude'] = lng
        stinfo_dict['elevation'] = elevation

        st_dict['station details'] = stinfo_dict
        all_stations.append(st_dict)


    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def stobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS)
        for the previous year."""

    # Query the dates and temperature observations 
    # of the most active station for the last year of data
    stat_sel = [Station.station, Station.name, Station.latitude, 
            func.round(Station.longitude,5), Station.elevation]

    mas = session.query(*stat_sel, func.count(Measurement.tobs)).\
            filter(Measurement.station == Station.station).\
            group_by(Measurement.station).\
            order_by(func.count('*').desc()).first()

    tobs_1y = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date >= year_ago).\
            filter(Measurement.station == mas[0]).\
            order_by(Measurement.date).all()

    session.close()

    # Dictionary for station info
    stinfo_dict = {}
    stinfo_dict['station ID'] = mas[0]
    stinfo_dict['name'] = mas[1]
    stinfo_dict['latitude'] = mas[2]
    stinfo_dict['longitude'] = mas[3]
    stinfo_dict['elevation'] = mas[4]

    # Dictionary for tempearure observations
    tobs_dict = {}
    for date, tobs in tobs_1y:
        tobs_dict[date] = tobs

    # Main dictionary
    all_tobs = {}
    all_tobs['station information'] = stinfo_dict
    all_tobs['temperature observations'] = tobs_dict

    return jsonify(all_tobs)
    

@app.route("/api/v1.0/<start>")
def temp_analysis_1(start):
    """Return a JSON list of the minimum temperature, the average temperature,
         and the max temperature for a given start date."""
    
    # Return a JSON list if start date supplied by user
    # falls beetween first and last date, or a 404 if not
    if start in date_list:
        # Create our session (link) from Python to the DB
        session = Session(engine)

        temps1 = session.query(func.min(Measurement.tobs), 
                func.round(func.avg(Measurement.tobs),2), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

        session.close()
        
        # Date range dictionary
        tempdates_dict = {}
        tempdates_dict['start date'] = start
        tempdates_dict['end date'] = last_date[0]
                
        # Temperatures dictionary
        temps_dict = {}
        for tmin, tavg, tmax in temps1:
            temps_dict['minimum temperature'] = tmin
            temps_dict['average temperature'] = tavg
            temps_dict['maximum temperature'] = tmax

        # Main dictionary
        tanalysis1_dict = {}
        tanalysis1_dict['date range'] = tempdates_dict
        tanalysis1_dict['temperatures'] = temps_dict

        return jsonify(tanalysis1_dict)
    
    return jsonify({"error": f"Date should be between {first_date[0]} and {last_date[0]}"}), 404


@app.route("/api/v1.0/<start>/<end>")
def temp_analysis_2(start, end):
    """Return a JSON list of the minimum temperature, the average temperature,
       and the max temperature for a range between given start and end date."""
   
    # Return a JSON list if start date or end date supplied by user
    # fall beetween first and last date, and if order is correct
    # or a 404 if not
    if start in date_list and end in date_list:
        # Convert start and end dates to datetime
        start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
        end_dt = dt.datetime.strptime(end, '%Y-%m-%d')
        # Check if start date is before end date
        if start_dt <= end_dt:
            # Create our session (link) from Python to the DB
            session = Session(engine)

            temps2 = session.query(func.min(Measurement.tobs), 
                    func.round(func.avg(Measurement.tobs),2), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

            session.close()

            # Date range dictionary
            tempdates_dict = {}
            tempdates_dict['start date'] = start
            tempdates_dict['end date'] = end
         
            # Temperatures dictionary
            temps_dict = {}
            for tmin, tavg, tmax in temps2:
                temps_dict['minimum temperature'] = tmin
                temps_dict['average temperature'] = tavg
                temps_dict['maximum temperature'] = tmax

            # Main dictionary
            tanalysis2_dict = {}
            tanalysis2_dict['date range'] = tempdates_dict
            tanalysis2_dict['temperatures'] = temps_dict

            return jsonify(tanalysis2_dict)

    return jsonify({"error": f"Dates should be between {first_date[0]} and {last_date[0]}, and start date should be before end date"}), 404



if __name__ == '__main__':
    app.run(debug=True)
