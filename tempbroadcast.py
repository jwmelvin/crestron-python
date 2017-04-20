#! /usr/bin/python

import forecastio
import datetime
import socket

def main():

	api_key = "YOUR_API_KEY_HERE"
	lat = 38.9136980
	lng = -77.1576710

	forecast = forecastio.load_forecast(api_key, lat, lng)

	print "Broadcasting: {}".format(int(round(10*forecast.currently().temperature,0)))
	
#	host = '127.0.0.1'
	host = '<broadcast>'
	port = 60000
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('', 0))
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto(str(int(round(10*forecast.currently().temperature,0))),(host,port))
			

if __name__ == "__main__":
    main()
