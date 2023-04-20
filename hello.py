from flask import Flask, render_template, request, url_for
from datetime import datetime, timedelta
import requests
import json
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import matplotlib
from matplotlib import pyplot as plt
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)

engine = create_engine('sqlite:///stocks.db')
#Session = sessionmaker(bind=engine)
#session = Session()

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stockdetails'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    symbol = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

Base.metadata.create_all(engine)

@app.route('/')
def index():
    # Retrieve the latest data from the database
    return render_template('index.html')


@app.route('/visualize.html', methods=['POST'])
def visualization():
    conn = sqlite3.connect('stocks.db')
    cur = conn.cursor()
    data = request.form.get('dataTab').split()
    chart_query = "SELECT date, close FROM stockdetails WHERE symbol = '" + data[0] + "' AND date >= '" + data[1] + "'"
    cur.execute(chart_query)
    date_vals = cur.fetchall()
    dates = [i for i, j in date_vals]
    cl_pr = [round(j, 2) for i, j in date_vals]

    fig, ax = plt.subplots()
    ax.plot(dates, cl_pr)

    plt.title(data[0]+' Share Price Chart')
    ax.set_xticklabels([])
    plt.show()
    return render_template('visualize.html')






@app.route('/stocks.html', methods=['POST'])
def fetch_stocks():
    conn = sqlite3.connect('stocks.db')
    cur = conn.cursor()
    time_frame = request.form.get('time_frame')
    stock_symbol = request.form.get('symbol')
    if time_frame == '1 month':
        dateFilter = datetime.now() - timedelta(days=30)
    elif time_frame == '3 months':
        dateFilter = datetime.now() - timedelta(days=91)
    elif time_frame == '6 months':
        dateFilter = datetime.now() - timedelta(days=182)
    elif time_frame == '1 year':
        dateFilter = datetime.now() - timedelta(days=365)
    dateFilter = dateFilter.date()
    fe = "SELECT * FROM stockdetails WHERE symbol = '" + stock_symbol + "' AND date >= '" + str(dateFilter) + "'"
    cur.execute(fe)
    data = cur.fetchall()
    query_inp = stock_symbol+" "+str(dateFilter)
    return render_template('stocks.html', data=data, query_inp=query_inp )




@app.route('/update_data')
def update_stocks():
    # Make the API request and get the data

    conn = sqlite3.connect('stocks.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM stockdetails")

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": "",
        "outputsize": "full", 
        "apikey": "3SFEIJELT3TIH47P"
    }
    symbol = ["AAPL","MSFT","GOOG","AMZN"]
    for i in symbol:    
        params["symbol"] = i
        print(params)
        response = requests.get(url, params=params)
        data = json.loads(response.text)

        # Get the data from the past year and store it in the database
        start_date = datetime.now() - timedelta(days=365)
        for date_str, values in data["Time Series (Daily)"].items():
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if date > start_date:
                a = datetime.strptime(str(date)[:-9], '%Y-%m-%d').date()
                value_tuple = (
                    a,
                    params["symbol"],
                    float(values["1. open"]),
                    float(values["2. high"]),
                    float(values["3. low"]),
                    float(values["4. close"]),
                    int(values["6. volume"]),
                )
                cur.execute("INSERT INTO stockdetails (date, symbol, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)", value_tuple)
    conn.commit()
    return render_template('index.html')





if __name__ == '__main__':
    app.run(debug=True)



