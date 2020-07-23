import json
import numpy as np
import pandas as pd
from flask import Flask, render_template
from scipy.optimize import curve_fit
from scipy.stats import linregress
from sqlalchemy import create_engine
from sqlalchemy import MetaData

app = Flask(__name__)

# Connect to Sqlite
engine = create_engine("sqlite:///scrape/everymac.db")
metadata = MetaData()
metadata.reflect(bind=engine)
# Read tables, divide by screen size
table_name = list(metadata.tables)[0]
macbooks = pd.read_sql_table(table_name, engine)
macbooks_13 = macbooks[macbooks["name"].str.contains('13"')]
macbooks_15 = macbooks[macbooks["name"].str.contains('15"')]
macbooks_17 = macbooks[macbooks["name"].str.contains('17"')]

# Macbook Price over time
price_data = macbooks_15[["price"]].copy()
price_data.index = pd.to_datetime(macbooks_15["introduced"])
price_data["price"] = price_data["price"].str.split(",").str.get(0)
price_data["price"] = price_data["price"].str.split("-").str.get(0)
price_data["price"] = price_data["price"].str.replace("$", "")
price_data = price_data.groupby(["introduced"]).min()
price_data["days"] = (price_data.index - price_data.index.min()).astype('timedelta64[D]')
price_data.index = price_data.index.strftime('%Y-%m-%d')
price_data["x"] = price_data.index
price_data["y"] = price_data["price"]
(slope, intercept, rvalue, pvalue, stderr) = linregress(price_data["days"], price_data.price.astype(int))
price_data["reg_x"] = price_data.index
price_data["reg_y"] = price_data["days"] * slope + intercept


# Macbook RAM over Time
ram_data = macbooks_15[["ram"]].copy()
ram_data["introduced"] = pd.to_datetime(macbooks_15["introduced"])
ram_data["unit"] = ram_data["ram"].str.split(" ").str.get(1)
ram_data["ram_original"] = ram_data["ram"]
ram_data["ram"] = ram_data["ram"].str.split(" ").str.get(0)
mb = ram_data[ram_data["unit"].str.find("MB") != -1]["ram"].astype(int)/1024
ram_data.loc[mb.index, ["ram"]] = ram_data["ram"].astype(int)/1024
ram_data["ram"] = ram_data["ram"].astype(float)
ram_data = ram_data.groupby(["introduced"]).min()
ram_data["days"] = (ram_data.index - ram_data.index.min()).astype('timedelta64[D]')
z = np.polyfit(ram_data["days"], ram_data["ram"], 2)
f = np.poly1d(z)
y_exp = f(ram_data["days"])
ram_data["x"] = ram_data.index.strftime('%Y-%m-%d')
ram_data["y"] = ram_data["ram"]
ram_data["reg_x"] = ram_data["x"]
ram_data["reg_y"] = y_exp

# Macbook $USD per GB of RAM over Time
ram_price_data = macbooks_15[["introduced", "ram", "price"]].copy()
ram_price_data["introduced"] = pd.to_datetime(ram_price_data["introduced"])
ram_price_data["ram_unit"] = ram_price_data["ram"].str.split(" ").str.get(1)
ram_price_data["ram"] = ram_price_data["ram"].str.split(" ").str.get(0)
mb_index = ram_price_data[ram_price_data["ram_unit"].str.find("MB") != -1]
ram_price_data.loc[mb_index.index, ["ram"]] = ram_price_data["ram"].astype(int)/1024
ram_price_data["ram"] = ram_price_data["ram"].astype(float)
ram_price_data = ram_price_data.groupby(["introduced"]).min()
ram_price_data["days"] = (ram_price_data.index - ram_price_data.index.min()).astype('timedelta64[D]')
ram_price_data["price"] = ram_price_data["price"].str.split(" ").str.get(0)
ram_price_data["price"] = ram_price_data["price"].str.replace(",", "")
ram_price_data["price"] = ram_price_data["price"].str.replace("$", "")
ram_price_data["price"] = ram_price_data["price"].astype(int)
ram_price_data["price"] = ram_price_data["price"]/ram_price_data["ram"]
def func(x, a, b): return a/(b**x)
popt, pcov = curve_fit(func, ram_price_data["days"], ram_price_data["price"])
x = pd.date_range(ram_price_data.index.min(), ram_price_data.index.max())
y_exp = func(range(ram_price_data["days"].max()),popt[0],popt[1])
ram_price_data_json = {}
ram_price_data_json["x"] = list(ram_price_data.index.strftime('%Y-%m-%d'))
ram_price_data_json["y"] = list(ram_price_data["price"])
ram_price_data_json["reg_x"] = list(x.strftime('%Y-%m-%d'))
ram_price_data_json["reg_y"] = list(y_exp)

# Macbook storage over Time
storage_data = macbooks_15[["storage"]].copy()
storage_data["introduced"] = pd.to_datetime(macbooks_15["introduced"])
storage_data["storage"] = storage_data["storage"].str.split(" ").str.get(0)
storage_data["storage"] = storage_data["storage"].str.replace(",", "")
storage_data["storage"] = storage_data["storage"].astype(int)
storage_data = storage_data.groupby(["introduced"]).min()
storage_data["days"] = (storage_data.index - storage_data.index.min()).astype('timedelta64[D]')
z = np.polyfit(storage_data["days"], storage_data["storage"], 3)
f = np.poly1d(z)
y_exp = f(storage_data["days"])
storage_data["x"] = storage_data.index.strftime('%Y-%m-%d')
storage_data["y"] = storage_data["storage"]
storage_data["reg_x"] = storage_data["x"]
storage_data["reg_y"] = y_exp

# Macbook $USD per GB of storage over Time
storage_price_data = macbooks_15[["introduced", "storage", "price"]].copy()
storage_price_data["introduced"] = pd.to_datetime(storage_price_data["introduced"])
storage_price_data["storage"] = storage_price_data["storage"].str.split(" ").str.get(0)
storage_price_data["storage"] = storage_price_data["storage"].str.replace(",", "")
storage_price_data["storage"] = storage_price_data["storage"].astype(int)
storage_price_data = storage_price_data.groupby(["introduced"]).min()
storage_price_data["days"] = (storage_price_data.index - storage_price_data.index.min()).astype('timedelta64[D]')
storage_price_data["price"] = storage_price_data["price"].str.split(" ").str.get(0)
storage_price_data["price"] = storage_price_data["price"].str.replace(",", "")
storage_price_data["price"] = storage_price_data["price"].str.replace("$", "")
storage_price_data["price"] = storage_price_data["price"].astype(int)
storage_price_data["price"] = storage_price_data["price"]/storage_price_data["storage"]
def func(x, a, b): return a/(b**x)
popt, pcov = curve_fit(func, storage_price_data["days"], storage_price_data["price"])
x = pd.date_range(storage_price_data.index.min(), storage_price_data.index.max())
y_exp = func(range(storage_price_data["days"].max()),popt[0],popt[1])
storage_price_data_json = {}
storage_price_data_json["x"] = list(storage_price_data.index.strftime('%Y-%m-%d'))
storage_price_data_json["y"] = list(storage_price_data["price"])
storage_price_data_json["reg_x"] = list(x.strftime('%Y-%m-%d'))
storage_price_data_json["reg_y"] = list(y_exp)

@app.route("/")
def home():
    return render_template("./index.html")

@app.route("/index.html")
def index():
    return render_template("./index.html")

@app.route("/data.html")
def data():
    return render_template("./data.html")

@app.route("/data.js")
def data_js():
    return "data = `" + str(macbooks.to_html()) + "`"

@app.route("/visualizations/memory.html")
def memory():
    return render_template("./visualizations/memory.html")

@app.route("/data/memory.js")
def memory_js():
    return "data = " + str(ram_data.to_json())

@app.route("/visualizations/storage.html")
def storage():
    return render_template("./visualizations/storage.html")

@app.route("/data/storage.js")
def storage_js():
    return "data = " + str(storage_data.to_json())

@app.route("/visualizations/memory_price.html")
def memory_price():
    return render_template("./visualizations/memory_price.html")

@app.route("/data/memory_price.js")
def memory_price_js():
    return "data = " + json.dumps(ram_price_data_json)

@app.route("/visualizations/storage_price.html")
def storage_price():
    return render_template("./visualizations/storage_price.html")

@app.route("/data/storage_price.js")
def storage_price_js():
    return "data = " + json.dumps(storage_price_data_json)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)