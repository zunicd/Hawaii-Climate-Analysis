# Hawaii Climate Analysis

### 1. Climate Analysis and Exploration

We used Python and SQLAlchemy to do basic climate analysis and data exploration of Hawaii climate database. 

This part is covered in the notebook *hawaii_climate.ipynb*.

#### Precipitation Analysis

- We designed a query to retrieve the last 12 months of precipitation data and selected only the `date` and `prcp` values.
- The query results were loaded into a Pandas Dataframe and the index was set to the date column.
- The Dataframe values were sorted by `date` and the results were plotted using the DataFrame `plot` method.

#### Station Analysis

Several queries were designed:

- a query to calculate the total number of stations.
- a query to find the most active stations..
- a query to retrieve the last 12 months of temperature observation data (TOBS).

The last query was filtered by the station with the highest number of observations and results were plotted as a histogram with `bins=12`.

#### Temperature Analysis I

Hawaii is reputed to enjoy mild weather all year. Is there a meaningful difference between the temperature in, for example, June and December?

- First, the average temperatures in June and in December at all stations across all available years in the dataset were identified. 
- And the t-test was used to determine whether the difference in the means, if any, is statistically significant. It is.

#### Temperature Analysis II

- The function called `calc_temps` will accept a start date and end date in the format `%Y-%m-%d`. It will return the minimum, average, and maximum temperatures for that range of dates.
- The function`calc_temps` was used to calculate the min, avg, and max temperatures for the date range matching dates from the previous year.
- The min, avg, and max temperature from the previous query were plotted as a bar chart. The average temperature was used as the bar height, and the peak-to-peak (TMAX-TMIN) value as the y error bar (YERR).

#### Daily Rainfall Average

- The rainfall per weather station was calculated using the previous year's matching dates.
- The daily normals were calculated. Normals are the averages for the min, avg, and max temperatures.
- The function `daily_normals`calculates the daily normals for a specific date. This date string will be in the format `%m-%d`. All historic TOBS that match that date string were used.
- A list of dates for the date range was created in the format `%m-%d`. The `daily_normals` function was used to calculate the normals for each date string and append the results to a list.
- The list of daily normals was loaded into a Pandas Dataframe, the index was set equal to the date and  Pandas was used to plot an area plot (`stacked=False`) for the daily normals.



### 2. Climate App

*A* Flask API (the script *app.py*) was designed based on the queries that developed in the first part. To run it type:

`pyton app.py`

in the terminal and open web page `127.0.0.1:5000` plus one of below listed routes.

##### Routes

The following routes were created using Flask:

- **/**

  Home page - lists all routes that are available:

```
Available Routes:
/api/v1.0/precipitation
/api/v1.0/stations
/api/v1.0/tobs
/api/v1.0/2016-10-09
/api/v1.0/2016-10-09/2016-10-30
```

- ***/api/v1.0/precipitation***
  Converts the query results to a dictionary using `date` as the key and `prcp` as the value and returns the JSON representation of the dictionary:

```
[
  {
    "2016-08-23": 0.0
  }, 
  {
    "2016-08-23": 0.15
  }, 
  ...
```

- ***/api/v1.0/stations***

  Returns a JSON list of stations from the dataset:

```
[
  {
    "station ID": "USC00519397", 
    "station details": {
      "elevation": 3.0, 
      "latitude": 21.2716, 
      "longitude": -157.8168, 
      "name": "WAIKIKI 717.2, HI US"
    }
  }, 
  {
    "station ID": "USC00513117", 
    "station details": {
    ...
```

- ***/api/v1.0/tobs***

  Queries the dates and temperature observations of the most active station for the last year of data and returns a JSON list of temperature observations (TOBS) for the previous year.

```
{
  "station information": {
    "elevation": 32.9, 
    "latitude": 21.45167, 
    "longitude": -157.84889, 
    "name": "WAIHEE 837.5, HI US", 
    "station ID": "USC00519281"
  }, 
  "temperature observations": {
    "2016-08-23": 77.0, 
    "2016-08-24": 77.0, 
    ...
```

- ***/api/v1.0/\<start>*** and ***/api/v1.0/\<start>/\<end>***

  Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

  When given the <u>start only</u>, calculates `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date:

```
{
  "date range": {
    "end date": "2017-08-23", 
    "start date": "2016-10-09"
  }, 
  "temperatures": {
    "average temperature": 74.08, 
    "maximum temperature": 87.0, 
    "minimum temperature": 58.0
  }
}
```

​	When given the <u>start and the end dat</u>e, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start 	and end date inclusive:

```
{
  "date range": {
    "end date": "2016-10-30", 
    "start date": "2016-10-09"
  }, 
  "temperatures": {
    "average temperature": 77.01, 
    "maximum temperature": 81.0, 
    "minimum temperature": 68.0
  }
}
```



### Tools / Techniques Used:

- Python
- Pandas
- Matplotlib
- Jupyter Notebook
- SQLAlchemy
- Flask
- SQLite
- Numpy
- SciPy



### About Data

 Two tables in SQLite database have been provided for this project. 

1. ***measurement*** - contains precipitation and temperature information for every day and station:

- **Number of records:**      19,550
- **Columns**:
  - station
  - date
  - prcp
  - tobs

2. ***station*** - contains station information:

- **Number of records:**    9

- **Columns**:

  - station
  - name
  - latitude
  - longitude
  - elevation

  



