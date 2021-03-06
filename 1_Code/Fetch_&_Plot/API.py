# Api Backend
import plotly.plotly as py #Plotly Api
import plotly.figure_factory as go
import ArrayNCalc
import Main
import RSI
import plotly.graph_objs as obj
import time #To get time and date
import pandas_datareader.data as web #Database Reader
import json # JavaScript Object Notation
import LinearAlgebra # Linear Algebra File
import numpy as np #Numpy for Matrix Handling
import Fetching #Fetching File
import Graphing #Graphing File
from flask import Flask, render_template, request, jsonify, make_response, send_file
import feedparser
from yahoo_finance import Share #Yahoo Finance Api
from datetime import datetime # Date
from datetime import timedelta # Adding to date
from plotly.graph_objs import * #Plotly Objects
import numpy
import Cache2
import os
import sys


Cache2.MakeTable()								# MAKE THE TABLE FIRST PLZ	

app = Flask(__name__)

# main function, initialize web app with IP and port
if __name__ == '__main__':

	app.run(host = "127.0.0.1", port = 4000, debug = False)

# Function by Jake, gets the current price of any stock (using yahoo finance API)
# receives a stock symbol in the form of a string. The Share(Sym) function takes this string and turns it into a special type in the yahoo finance library, which contains stock share information.
# The get_price() function returns a string that contains the current price of the given company's stock.
def getCurrentPrice(Sym):
	ticker = Share(Sym)
	return ticker.get_price()

#Function by  Jake, gets tht percent change in price of the stock (using yahoo finance API)
# receives a stock symbol in the form of a string. The Share(Sym) function takes this string and turns it into a special type in the yahoo finance library, which contains stock share information.
# The get_percent_change function returns a string that contains the percent change of the given company's stock.
def getPercentChange(Sym):
	ticker = Share(Sym)
	return ticker.get_percent_change()

#Function by Jake, returns the name of the source of the RSS feed, "Yahoo! Finance: News"(from yahoo finance RSS feed, deciphered using a feedparser)
# this function is sent a feed of a special type defined in the feedparser library, which contains information from the RSS feed of the given company.
# the indexes 'feed' and 'title' return the title from the feed variable
def getNewsTitle(feed):
	return feed['feed']['title']

# Function by Jake, gets the top n news headlines for the given stock (from yahoo finance RSS feed, deciphered using a feedparser)
# this function is sent a feed of a special type defined in the feedparser library, which contains information from the RSS feed of the given company.
# the indexes 'entries', 'n' and 'title' returns the titles for the 'n' most recent entries on the feed
def getNews(feed, n):
	return feed['entries'][n]['title']

# Function by Jake, gets link for the top n newsheadlines for the given stock (from yahoo finance RSS feed, deciphered using a feedparser) 
# the indexes 'feed' and 'title' return the title from the feed variable
# the indexes 'entries', 'n' and 'link' returns the links for the 'n' most recent entries on the feed
def getLink(feed, n):
	return feed['entries'][n]['link']

# Used for displaying the current price and percent change of the given stock
@app.route('/ticker/') # @app.route is used to route URLs to code
def ticker():
	tick = request.args.get('s') #used to assign the company name to a variable
	feed = feedparser.parse('http://finance.yahoo.com/rss/headline?s=%s' %tick) #parses the RSS feed of the company with symbol saved in "tick"
	ret = "The current price of " + tick + " is $" + getCurrentPrice(tick) + ". This is a " + getPercentChange(tick) + " change."
	return ret

# Used for displaying the top news headlines for the given stock (using yahoo finance RSS feed and feed parser)
@app.route('/news/')
def news():
	tick = request.args.get('s') #used to assign company name to a variable
	feed = feedparser.parse('http://finance.yahoo.com/rss/headline?s=%s' %tick)  #parses the RSS feed of the company with symbol saved in "tick"
	
	a = "<a href='" + getLink(feed, 0) + "'>" + getNews(feed, 0) + " </a> <br>"  #prints the appropriate link
	b = "<a href='" + getLink(feed, 1) + "'>" + getNews(feed, 1) + " </a> <br>"
	c = "<a href='" + getLink(feed, 2) + "'>" + getNews(feed, 2) + " </a> <br>"
	return a + b + c

# Api To Get Graph
@app.route('/graph/')
def getGraph():
	stockName = request.args.get('s')
	var=stockName
	old_stdout = sys.stdout
	sys.stdout = open(os.devnull, "w")
	if var != 'null':					# ONLY PRECEDE IF WE HAVE A COMPANY
	
			
			Coefficients = numpy.zeros((11,1))
			
			timeBegin=2010
			
			totalDataCurrent=Fetching.fetchDataToday(var,timeBegin) # This gets all the data from the start year to 3 days ago (give or take a work day)

			googData=Fetching.fetchGoogData(var) # Fetch Todays data from google finance
			
			Prediction_Data=Fetching.fetchDataSpec(var,(datetime.now()+timedelta(days=-45))) # Get the data from just the past month for the prediciton part
			
			Prediction_Data_Length=len(Prediction_Data.Close) # Lenght of the predictin Data to save the recalc of it

			
			Coefficients=LinearAlgebra.coeffcients_Generator(LinearAlgebra.makeXVals_Matrix(10,timeBegin,Prediction_Data_Length),LinearAlgebra.makeY_Matrix(Prediction_Data.Low)) #coeffcients for prediction fucntion a0-a10		
			
			
			
			
			Prediction_Model=LinearAlgebra.makeOutY(Coefficients,Prediction_Data_Length,timeBegin,totalDataCurrent.High,googData) # Gets Prediciton Model or scatter of predicted points these points are also normalized
			
			pointY=LinearAlgebra.getPointY(Coefficients,timeBegin,googData[0]['LastTradePrice'],totalDataCurrent.High[len(totalDataCurrent)-1]) #gets Predictiion Point for the next day independently so I can calculate individual days
			
			R=RSI.PredictRSI(totalDataCurrent.Close)

			pointY=LinearAlgebra.getPointY(Coefficients,timeBegin,googData[0]['LastTradePrice'],totalDataCurrent.Low[len(totalDataCurrent)-1]) #gets Predictiion Point for the next day independently so I can calculate individual days
			
			url=Graphing.totalTogether(var,totalDataCurrent,googData,Prediction_Model,pointY,R) #Print Final Graph with everything together
			
			url = url + ".embed?width=640&height=480"
			ret = "<iframe width='640' height='480' frameborder='0' scrolling='no' src='" + url + "'> </iframe>"
			sys.stdout.close()
			sys.stdout = old_stdout
			return ret
	else:
		sys.stdout.close()
		sys.stdout = old_stdout
		return "false"

@app.route('/acc/')
def getAcc():
	stockName = request.args.get('s')
	old_stdout = sys.stdout
	sys.stdout = open(os.devnull, "w")
	var="AAPL"

	var=stockName
	if var != 'null':					# ONLY PRECED IF WE HAVE A COMPANY
		timeBegin=2010
			
		totalDataCurrent=Fetching.fetchDataToday(var,timeBegin) # This gets all the data from the start year to 3 days ago (give or take a work day)

		googData=Fetching.fetchGoogData(var) # Fetch Todays data from google finance
			
		Prediction_Data=Fetching.fetchDataSpec(var,(datetime.now()+timedelta(days=-45))) # Get the data from just the past month for the prediciton part
			
		Prediction_Data_Length=len(Prediction_Data.High) # Lenght of the predictin Data to save the recalc of it

		
		Coefficients=LinearAlgebra.coeffcients_Generator(LinearAlgebra.makeXVals_Matrix(10,timeBegin,Prediction_Data_Length),LinearAlgebra.makeY_Matrix(Prediction_Data.Low)) #coeffcients for prediction fucntion a0-a10		
		
		
		
		Prediction_Model=LinearAlgebra.makeOutY(Coefficients,Prediction_Data_Length,timeBegin,totalDataCurrent.High,googData) # Gets Prediciton Model or scatter of predicted points these points are also normalized
		
		ret = str(ArrayNCalc.CalculateConfidenceRating(Prediction_Model,totalDataCurrent.High))
		sys.stdout.close()
		sys.stdout = old_stdout
		return "The total price accuracy is: " + ret + "%"
	else:
		sys.stdout.close()
		sys.stdout = old_stdout
		return ""

@app.route('/relAcc/')
def getRelativeAcc():
	stockName = request.args.get('s')
	var=stockName
	old_stdout = sys.stdout
	sys.stdout = open(os.devnull, "w")
	if var != 'null':					# ONLY PRECED IF WE HAVE A COMPANY
		timeBegin=2010
			
		totalDataCurrent=Fetching.fetchDataToday(var,timeBegin) # This gets all the data from the start year to 3 days ago (give or take a work day)
		
		googData=Fetching.fetchGoogData(var) # Fetch Todays data from google finance
			
		Prediction_Data=Fetching.fetchDataSpec(var,(datetime.now()+timedelta(days=-45))) # Get the data from just the past month for the prediciton part
			
		Prediction_Data_Length=len(Prediction_Data.High) # Lenght of the predictin Data to save the recalc of it
		
		
		Coefficients=LinearAlgebra.coeffcients_Generator(LinearAlgebra.makeXVals_Matrix(10,timeBegin,Prediction_Data_Length),LinearAlgebra.makeY_Matrix(Prediction_Data.Low)) #coeffcients for prediction fucntion a0-a10		
		
		Prediction_Model=LinearAlgebra.makeOutY(Coefficients,Prediction_Data_Length,timeBegin,totalDataCurrent.High,googData) # Gets Prediciton Model or scatter of predicted points these points are also normalized
		
		
		ret = str(ArrayNCalc.CalculateRelativeACC(Prediction_Model,Prediction_Data.High))
		sys.stdout.close()
		sys.stdout = old_stdout
		return "The relative accuracy is: " + ret + "%"
	else:
		sys.stdout.close()
		sys.stdout = old_stdout
		return ""
													
#Cache2.PrintTable()													# Prints the Table											
#Cache2.return_cache_symbols("Symbol")										# pass the symbol of the company in the cache as a list
#Cache2.Search("Symbol")												# returns 1 ( true) or 0 (false) on whether the specified ticker is in cache
