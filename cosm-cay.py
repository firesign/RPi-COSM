#!/usr/bin/env python

# EEML updates to Cosm/Xively.
# by Michael LeBlanc
# generaleccentric.net
#
# May, 2013
# Last edit January 2018:
# Switched code from Xively/Cosm/Pachube to Cayenne

# Nodes:
#   1: Office  
#   2: MBL_room
#   3: LivingRoom
#   4: Pantry
#   5: Remote (shed)
#   6: Oil level sender
#   7: Oil level receiver
#  10: Garage
#  11: Kitchen

from __future__ import division

import re #regular expressions
import eeml
import eeml.datastream
import eeml.unit
import serial
import os
import time
import datetime
import sys
import urllib2
import threading #for gc routine
import gc #garbage collection
from eeml.datastream import CosmError

# Cayenne stuff *****************************************
import cayenne.client

# Cayenne authentication info.
MQTT_USERNAME = "29064280-aa93-11e7-a9b2-a5d7f5484bce"
MQTT_PASSWORD = "27926c04c28d1ebe246e6ce84af56096b27ddfae"
MQTT_CLIENT_ID = "f2cb3200-f3e6-11e7-b2d9-f97d29dc33e8"

# The callback for when a message is received from Cayenne.
def on_message(message):
    print("message received: " + str(message))
    # if there is an error processing the message return an error string, otherwise return nothing.

client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)
  
def main():
  
  global n1pointer, n1temps, n2pointer, n2temps, n3pointer, n3temps, n4pointer, n4temps
  n1pointer = 0
  n2pointer = 0
  n3pointer = 0
  n4pointer = 0
  n1temps = []
  n2temps = []
  n3temps = []
  n4temps = []

  # garbage collection to reduce memory leaks added July 2, 2014
  # gc is set to run every 21600 seconds (6 hours)
  
  #def foo():
  #  gc.collect()
  #  threading.Timer(21600, foo).start()
    
  
  def runningAverage(node, temperature, pointer, temps):
      #print "RunningAverage function; pointer = %d" % pointer
      total = 0
      # initially build-up the list of temperatures
      if len(temps) < 4:
        temps.extend([temperature])
        
        for j in range(0, (pointer + 1)):
          addend = float(temps[j])
          total = float(addend + total)
          avgx = total / (pointer + 1)
      # the list of temperatures is full, now replace the oldest one
      # with a new one
      else:
        temps[pointer] = temperature
        for j in range(0, 4):
          addend = float(temps[j])
          total = float(addend + total)
          avgx = total / 4
        
      average = round(avgx, 2)
      
      # increment  or reset pointer
      if pointer < 3:
        pointer += 1
      else:
        pointer = 0

      return (node, average, pointer, temps)
    

  def calcTemp():                    # routine to calculate single temperature units
    
    unkn = rawx.pop(0).strip()       # don't know what this is, drop for now
    place = nodeList[int(node)]      # substitute node for actual place in house

    wholeTemp = rawx.pop(0).strip()  # whole number part of temperature
    fracTemp = rawx.pop(0).strip()   # decimal part of temperature
    temperature = wholeTemp + "." + fracTemp
    
    return temperature               # pass this on!

  
  nodeList = 'Office', 'Garage', 'MBL_Room', 'In-law_Suite', 'Pantry', 'Kitchen'

  # CPU monitor routine, requires "import os"
  def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

  cpuTemp = int(float(getCPUtemperature()))
  
  
  # COSM variables. 
#  f = open('apikey.txt', 'r') 
#  API_KEY = f.read()
#  f.close() 
#  API_KEY = 'suinLKP1uD3GCkuUN-xBmvZzSzWSAKxEcnQrdUJyTHJRND0g'
#  FEED = 129833
   
#  API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)

  ser = serial.Serial('/dev/ttyUSB0', 57600)
  # ser.close()

  while True:
    client.loop()
          
    x = ser.readline()

    OKtest = re.match ( 'OK', x )         # match tests for match at beginning of string,
                                          # otherwise use search

    if OKtest:
      #pac = eeml.datastream.Cosm(API_URL, API_KEY)

      #print "Raw data received: " + x
      rawx = x.split()                    # split on whitespace

      ######################              # initial parsing
      ack = rawx.pop(0).strip()           # "OK": do nothing with it
      node = rawx.pop(0).strip()          # Node number
      
    
      if node == '1':
        
        tempLow = rawx.pop(0).strip()           # temperature low byte
        tempHigh = rawx.pop(0).strip()          # temperature high byte
        if int(tempHigh) < 5:			# if this byte is greater than 5, 
        				# temp is (for sure) a positive value
          tempRaw = (int(tempHigh) * 256) + int(tempLow)
        else:
          tempRaw = (255 ^ (int(tempLow))) * -1	# temp is negative value, so do a 1's complement
        tempRaw2 = tempRaw + 0.0
        actualTemp = tempRaw2 / 10
        
        humLow = rawx.pop(0).strip()            # humidity low byte
        humHigh = rawx.pop(0).strip()           # humidity high byte
        humRaw = (int(humHigh) * 256) + int(humLow)
        humRaw2 = humRaw + 0.0
        actualHum = humRaw2 / 10
        
        lightLow = rawx.pop(0).strip()            # humidity low byte
        lightHigh = rawx.pop(0).strip()           # humidity high byte
        lightRaw = (int(lightHigh) * 256) + int(lightLow)
        actualLight = lightRaw
        
        pir = rawx.pop(0).strip()               # PIR sensor 
        
        # Cayenne stuff:  ********************************
        #print("1: actualTemp: ", actualTemp)
        client.virtualWrite(1, actualTemp, "temp", "c")
        #print("2: actualHum: ", actualHum)
        client.virtualWrite(2, actualHum, "rel_hum", "p")
        #print("3: actualLight: ", actualLight)
        client.virtualWrite(3, actualLight, "lum", "p")
        #print("4: PIR: ", pir)
        client.virtualWrite(4, pir, "digital_sensor", "d")
        
        


      if node == '2':
        
        temperature = calcTemp()

        # Cayenne stuff:  ********************************
        client.virtualWrite(5, temperature, "temp", "c")
        
        # rolling average code:
        pointer = n2pointer
        temps = n2temps
        
        average = runningAverage(node, temperature, pointer, temps)
        node = average[0]
        avrg = average[1]
        pointer = average[2]
        temps = average[3]
        
        n2pointer = pointer
        n2temps = temps
        
        #print "Node: %s  Avg Temp: %s Celcius  Pointer: %s  List: %s" % (node, avrg, pointer, temps)
        
          

      elif node == '3':
        temperature = calcTemp()

        # Cayenne stuff:  ********************************
        client.virtualWrite(6, temperature, "temp", "c")
        
        # rolling average code:
        pointer = n3pointer
        temps = n3temps
        
        average = runningAverage(node, temperature, pointer, temps)
        node = average[0]
        avrg = average[1]
        pointer = average[2]
        temps = average[3]
        
        n3pointer = pointer
        n3temps = temps
        
        #print "Node: %s  Avg Temp: %s Celcius  Pointer: %s  List: %s" % (node, avrg, pointer, temps)
        


      elif node == '4':
        temperature = calcTemp()

        # Cayenne stuff:  ********************************
        client.virtualWrite(7, temperature, "temp", "c")
        
        # rolling average code:
        pointer = n4pointer
        temps = n4temps
        
        average = runningAverage(node, temperature, pointer, temps)
        node = average[0]
        avrg = average[1]
        pointer = average[2]
        temps = average[3]
        
        n4pointer = pointer
        n4temps = temps
    
        #print "Node: %s  Avg Temp: %s Celcius  Pointer: %s  List: %s" % (node, avrg, pointer, temps)
        
          

      elif node == '5':
        tempLow = rawx.pop(0).strip()           # temperature low byte
        tempHigh = rawx.pop(0).strip()          # temperature high byte
        if int(tempHigh) < 5:			# if this byte is greater than 5, 
						# temp is (for sure) a positive value
          tempRaw = (int(tempHigh) * 256) + int(tempLow)
        else:
          tempRaw = (255 ^ (int(tempLow))) * -1	# temp is negative value, so do a 1's complement
        tempRaw2 = tempRaw + 0.0
        actualTemp = tempRaw2 / 10
        
        humLow = rawx.pop(0).strip()            # humidity low byte
        humHigh = rawx.pop(0).strip()           # humidity high byte
        humRaw = (int(humHigh) * 256) + int(humLow)
        humRaw2 = humRaw + 0.0
        actualHum = humRaw2 / 10
        
        bvLow = rawx.pop(0).strip()              # batt volt low byte
        bvMid = rawx.pop(0).strip()              # batt volt mid byte
        bvHigh = rawx.pop(0).strip()             # batt volt high byte
        throwaway = rawx.pop(0).strip()          # throw away this byte
        bvRaw = (int(bvHigh) * 65536) + (int(bvMid) * 256) + int(bvLow)
        actualBv = bvRaw * 3.3 / 512			 # 512 or 1024, whichever works!
        Bv = round(actualBv, 2)

        spvLow = rawx.pop(0).strip()            # solarpanel low byte
        spvMid = rawx.pop(0).strip()            # solarpanel mid byte
        spvHigh = rawx.pop(0).strip()           # solarpanel high byte
        throwaway = rawx.pop(0).strip()         # throw away this byte
        spvRaw = (int(spvHigh) * 65536) + (int(spvMid) * 256) + int(spvLow)
        actualspv = spvRaw * 3.3 /512			# 512 or 1024, whichever works!
        Spv = round(actualspv, 2)

        # Cayenne stuff:  ********************************
        client.virtualWrite(8, actualTemp, "temp", "c")
        client.virtualWrite(9, actualHum, "rel_hum", "p")
        client.virtualWrite(10, Bv, "voltage", "v")
        client.virtualWrite(11, Spv, "voltage", "v")




      elif node == '6':                         # Oil Tank Level Sender
        oilLevel = rawx.pop(0).strip()

        client.virtualWrite(12, oilLevel, "tl", "gauge")
                
          
  
      elif node == '10':                        # Garage Node 10
        
        tempLow = rawx.pop(0).strip()           # temperature low byte
        tempHigh = rawx.pop(0).strip()          # temperature high byte
        if int(tempHigh) < 5:			# if this byte is greater than 5, 
						# temp is (for sure) a positive value
          tempRaw = (int(tempHigh) * 256) + int(tempLow)
        else:
          tempRaw = (255 ^ (int(tempLow))) * -1	# temp is negative value, so do a 1's complement
        tempRaw2 = tempRaw + 0.0
        actualTemp = tempRaw2 / 10              # Garage Temperature ***************

        humLow = rawx.pop(0).strip()            # humidity low byte
        humHigh = rawx.pop(0).strip()           # humidity high byte
        humRaw = (int(humHigh) * 256) + int(humLow)
        humRaw2 = humRaw + 0.0
        actualHum = humRaw2 / 10                # Garage Humidity ******************

        tempLow = rawx.pop(0).strip()           # temperature low byte
        tempHigh = rawx.pop(0).strip()          # temperature high byte
        if int(tempHigh) < 5:			# if this byte is greater than 5, 
						# temp is (for sure) a positive value
          tempRaw = (int(tempHigh) * 256) + int(tempLow)
        else:
          tempRaw = (255 ^ (int(tempLow))) * -1	# temp is negative value, so do a 1's complement
        tempRaw2 = tempRaw + 0.0
        actualTempWB = tempRaw2 / 10            # Wormbox Temperature **************

        humLow = rawx.pop(0).strip()            # humidity low byte
        humHigh = rawx.pop(0).strip()           # humidity high byte
        humRaw = (int(humHigh) * 256) + int(humLow)
        humRaw2 = humRaw + 0.0
        actualHumWB = humRaw2 / 10              # Wormbox Humidity *****************
        
        coLow = rawx.pop(0).strip()             # Carbon Monoxide high byte
        coHigh = rawx.pop(0).strip()            # Carbon Monoxide low byte
        coRaw = (int(coHigh) * 256) + int(coLow)
        actualco = coRaw
        #actualco = coRaw2 / 10                  # CO Level *************************
        
        # Garage Door Sensor Reading for Test
        gdLow = rawx.pop(0).strip()            # garage door low byte FOR TEST
        gdHigh = rawx.pop(0).strip()           # garage door high byte
        #gdRaw = (int(gdHigh) * 256) + int(gdLow)

        garageDoor = rawx.pop(0).strip()        # garage door

        client.virtualWrite(13, actualTemp, "temp", "c")
        client.virtualWrite(14, actualHum, "rel_hum", "p")
        client.virtualWrite(15, actualco, "co", "value")
        client.virtualWrite(16, garageDoor, "digital_sensor", "d")
        

        #print "Node: %s  CO2High: %s  CO2Low: %s  Garage Door: %s  LDRHigh: %s  LDRLow: %s" % (node, co2High, co2Low, garageDoor, ldrHigh, ldrLow)


        
      if node == '11':
        
        tempLow = rawx.pop(0).strip()           # temperature low byte
        tempHigh = rawx.pop(0).strip()          # temperature high byte
        if int(tempHigh) < 5:			# if this byte is greater than 5, 
        				# temp is (for sure) a positive value
          tempRaw = (int(tempHigh) * 256) + int(tempLow)
        else:
          tempRaw = (255 ^ (int(tempLow))) * -1	# temp is negative value, so do a 1's complement
        tempRaw2 = tempRaw + 0.0
        actualTemp = tempRaw2 / 10
        
        humLow = rawx.pop(0).strip()            # humidity low byte
        humHigh = rawx.pop(0).strip()           # humidity high byte
        humRaw = (int(humHigh) * 256) + int(humLow)
        humRaw2 = humRaw + 0.0
        actualHum = humRaw2 / 10
                
        bvLow = rawx.pop(0).strip()              # batt volt low byte
        bvMid = rawx.pop(0).strip()              # batt volt mid byte
        bvHigh = rawx.pop(0).strip()             # batt volt high byte
        throwaway = rawx.pop(0).strip()          # throw away this byte
        bvRaw = (int(bvHigh) * 65536) + (int(bvMid) * 256) + int(bvLow)
        actualBv = bvRaw * 3.3 / 1024
        Bv = round(actualBv, 2)

        spvLow = rawx.pop(0).strip()            # solarpanel low byte
        spvMid = rawx.pop(0).strip()            # solarpanel mid byte
        spvHigh = rawx.pop(0).strip()           # solarpanel high byte
        throwaway = rawx.pop(0).strip()         # throw away this byte
        spvRaw = (int(spvHigh) * 65536) + (int(spvMid) * 256) + int(spvLow)
        actualspv = spvRaw * 3.3 /1024
        Spv = round(actualspv, 2)
        
        client.virtualWrite(17, actualTemp, "temp", "c")
        client.virtualWrite(18, actualHum, "rel_hum", "p")
        client.virtualWrite(19, Bv, "voltage", "v")
        client.virtualWrite(20, Spv, "voltage", "v")
        

# call the main() function
if __name__ == '__main__':
  main()
