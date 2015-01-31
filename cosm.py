#!/usr/bin/env python

# EEML updates to Cosm/Xively.
# by Michael LeBlanc
# generaleccentric.net
#
# May, 2013
# Last edit October 2014

# Nodes:
#   1: Office  
#   2: MBL_room
#   3: In-Law_Suite
#   4: Pantry
#   5: Remote (shed)
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
# import threading #for gc routine
# import gc #garbage collection
from eeml.datastream import CosmError

  
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
  API_KEY = 'suinLKP1uD3GCkuUN-xBmvZzSzWSAKxEcnQrdUJyTHJRND0g'
  FEED = 129833
   
  API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)

  ser = serial.Serial('/dev/ttyUSB0', 57600)
  # ser.close()

  while True:
          
    x = ser.readline()

    OKtest = re.match ( 'OK', x )         # match tests for match at beginning of string,
                                          # otherwise use search

    if OKtest:
      pac = eeml.datastream.Cosm(API_URL, API_KEY)

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
        
        
        
        pac.update([eeml.Data('Office_Temp', actualTemp,
                              unit=eeml.Unit('celcius', 'basicSI', 'C')),
                    eeml.Data('Office_Humidity', actualHum,
                              unit=eeml.Unit('percent', 'basicSI', 'RH')),
                    eeml.Data('Office_LightLevel', actualLight,
                              unit=eeml.Unit('candela', 'basicSI', 'cd')),
                    eeml.Data('Office_PIR', pir,
                              unit=eeml.Unit('percent', 'basicSI', 'LIFE'))])
        
        try:
          pac.put()
        except Exception as e:
          print "Oops! Something went wrong. Error = {}".format(e)
        except CosmError, e:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 2: StandardError')
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          #print('ERROR: StandardError')
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 2: StandardError')
        except:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 2: StandardError')
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])


      if node == '2':
        temperature = calcTemp()
        
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
        
        pac.update([eeml.Data('MBL_Room', avrg, unit=eeml.Unit('celcius', 'basicSI', 'C'))])
        try:
          pac.put()
        except Exception as e:
          print "Oops! Something went wrong. Error = {}".format(e)
        except CosmError, e:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 2: StandardError')
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          #print('ERROR: StandardError')
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 2: StandardError')
        except:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 2: StandardError')
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])
          

      elif node == '3':
        temperature = calcTemp()
        
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
        
        pac.update([eeml.Data('In-Law_Suite', avrg, unit=eeml.Unit('celcius', 'basicSI', 'C'))])
        try:
          pac.put()
        except Exception as e:
          print "Oops! Something went wrong. Error = {}".format(e)
        except CosmError, e:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 3: StandardError')
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          #print('ERROR: StandardError')
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 3: StandardError')
        except:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 3: StandardError')
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])


      elif node == '4':
        temperature = calcTemp()
        
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
        
        pac.update([eeml.Data('Pantry', avrg, unit=eeml.Unit('celcius', 'basicSI', 'C'))])
        try:
          pac.put()
        except Exception as e:
          print "Oops! Something went wrong. Error = {}".format(e)
        except CosmError, e:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 4: StandardError')
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          #print('ERROR: StandardError')
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 4: StandardError')
        except:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 4: StandardError')
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])
          

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
        
        battVLow = rawx.pop(0).strip()          # battery high byte
        battVHigh = rawx.pop(0).strip()         # battery low byte
        battVRaw = (int(battVHigh) * 256) + int(battVLow)
        battVRaw2 = battVRaw + 0.0
        actualBattV = (3.3 * battVRaw2) / 512
        battV = round(actualBattV, 2)

        ds1820Low = rawx.pop(0).strip()            # DS1820 low byte
        ds1820High = rawx.pop(0).strip()           # DS1820 high byte
        ds1820Raw = (int(ds1820High) * 256) + int(ds1820Low)
        ds1820Raw2 = ds1820Raw + 0.0
        actualds1820 = ds1820Raw2 / 100
        if actualds1820 > 100:
          actualds1820 = 0.1

##        if ds1820High > 128:                      # code to account for negative temps
##          ds1820Raw = ~ ds1820Low
##          actualds1820 = ds1820Raw * -1.0 / 100
##        else:
##          ds1820Raw = ds1820Low + 0.0
##          actualds1820 = ds1820Raw / 100

        pac.update([eeml.Data('Remote_Temp', actualTemp,
                              unit=eeml.Unit('celcius', 'basicSI', 'C')),
                    eeml.Data('Remote_Humidity', actualHum,
                              unit=eeml.Unit('percent', 'basicSI', 'RH')),
                    eeml.Data('Remote_Batt_V', battV,
                              unit=eeml.Unit('volts', 'basicSI', 'V')),
                    eeml.Data('Remote_Batt_Temp', actualds1820,
                              unit=eeml.Unit('celcius', 'basicSI', 'C'))])
        try:
          pac.put()
        except Exception as e:
          print "Oops! Something went wrong. Error = {}".format(e)
        except CosmError, e:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 5: StandardError')
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          #print('ERROR: StandardError')
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 5: StandardError')
        except:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 5: StandardError')
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])


  
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
        

        #print "Node: %s  CO2High: %s  CO2Low: %s  Garage Door: %s  LDRHigh: %s  LDRLow: %s" % (node, co2High, co2Low, garageDoor, ldrHigh, ldrLow)

        pac.update([eeml.Data('G_Temp', actualTemp,
                              unit=eeml.Unit('celcius', 'basicSI', 'C')),
                    eeml.Data('G_Humidity', actualHum,
                              unit=eeml.Unit('percent', 'basicSI', 'RH')),
                    eeml.Data('G_Wormbox_Temp', actualTempWB,
                              unit=eeml.Unit('celcius', 'basicSI', 'C')),
                    eeml.Data('G_Wormbox_Humidity', actualHumWB,
                              unit=eeml.Unit('percent', 'basicSI', 'RH')),
                    eeml.Data('G_Carbon_Monoxide', actualco,
                              unit=eeml.Unit('/1024', 'basicSI', '/1024')),
                    #eeml.Data('G_Door_Reading', gdRaw, unit=eeml.Unit('/1024', 'basicSI', '/1024')),
                    eeml.Data('G_Door_CLOSED', garageDoor,
                              unit=eeml.Unit('binary', 'basicSI', 'binary'))])
        
        
        try:
          pac.put()
        except Exception as e:
          print "Oops! Something went wrong. Error = {}".format(e)
        except CosmError, e:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 5: StandardError')
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          #print('ERROR: StandardError')
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 5: StandardError')
        except:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 5: StandardError')
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])

      else:
        rr = 0
        
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
        
        
        
        pac.update([eeml.Data('Kitchen_Temp', actualTemp,
                              unit=eeml.Unit('celcius', 'basicSI', 'C')),
                    eeml.Data('Kitchen_Humidity', actualHum,
                              unit=eeml.Unit('percent', 'basicSI', 'RH')),
                    eeml.Data('KitchenBattVolt', Bv,
                              unit=eeml.Unit('voltage', 'basicSI', 'V')),
                    eeml.Data('KitchenSolarVolt', Spv,
                              unit=eeml.Unit('voltage', 'basicSI', 'V'))])
        
        try:
          pac.put()
        except Exception as e:
          print "Oops! Something went wrong. Error = {}".format(e)
        except CosmError, e:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 2: StandardError')
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          #print('ERROR: StandardError')
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 2: StandardError')
        except:
          now = datetime.datetime.now()
          print now.strftime('%Y-%m-%d %H:%M ERROR Node 2: StandardError')
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])  
  

# call the main() function
if __name__ == '__main__':
  main()
