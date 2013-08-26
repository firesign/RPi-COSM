#!/usr/bin/env python

# EEML updates to Cosm/Xively.
# by Michael LeBlanc
# generaleccentric.net
#
# May, 2013

from __future__ import division

import re #regular expressions
import eeml
import eeml.datastream
import eeml.unit
import serial
import os
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

  
  nodeList = 'n', 'Garage', 'MBL_Room', 'In-law_Suite', 'Node4', 'Battery_Test'

  # CPU monitor routine, requires "import os"
  def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

  cpuTemp = int(float(getCPUtemperature()))
  
  
  # COSM variables. 
  API_KEY = 'suinLKP1uD3GCkuUN-xBmvZzSzWSAKxEcnQrdUJyTHJRND0g'
  FEED = 129833
   
  API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)

  ser = serial.Serial('/dev/ttyUSB0', 57600)

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
        temperature = calcTemp()
        
        # rolling average code:
        pointer = n1pointer
        temps = n1temps
        
        average = runningAverage(node, temperature, pointer, temps)
        node = average[0]
        avrg = average[1]
        pointer = average[2]
        temps = average[3]
        
        n1pointer = pointer
        n1temps = temps
        
        #print "Node: %s  Avg Temp: %s Celcius  Pointer: %s  List: %s" % (node, avrg, pointer, temps)
        
        pac.update([eeml.Data('Garage', avrg, unit=eeml.Unit('celcius', 'basicSI', 'C'))])
        try:
          pac.put()
        except CosmError, e:
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          print('ERROR: StandardError')
        except:
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])


      elif node == '2':
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
        except CosmError, e:
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          print('ERROR: StandardError')
        except:
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
        except CosmError, e:
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          print('ERROR: StandardError')
        except:
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
        except CosmError, e:
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          print('ERROR: StandardError')
        except:
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])

      elif node == '5':
        tempLow = rawx.pop(0).strip()           # temperature low byte
        tempHigh = rawx.pop(0).strip()          # temperature high byte
        tempRaw = (int(tempHigh) * 256) - 1 + int(tempLow)
        tempRaw2 = tempRaw + 0.0
        actualTemp = tempRaw2 / 10
        
        humLow = rawx.pop(0).strip()            # humidity low byte
        humHigh = rawx.pop(0).strip()           # humidity high byte
        humRaw = (int(humHigh) * 256) - 1 + int(humLow)
        humRaw2 = humRaw + 0.0
        actualHum = humRaw2 / 10
        
        battVLow = rawx.pop(0).strip()          # battery high byte
        battVHigh = rawx.pop(0).strip()         # battery low byte
        battVRaw = (int(battVHigh) * 256) - 1 + int(battVLow)
        battVRaw2 = battVRaw + 0.0
        actualBattV = (3.3 * battVRaw2) / 512
        battV = round(actualBattV, 2)

        pac.update([eeml.Data('N5_Temperature', actualTemp,
                              unit=eeml.Unit('celcius', 'basicSI', 'C')),
                    eeml.Data('N5_Humidity', actualHum,
                              unit=eeml.Unit('percent', 'basicSI', 'RH')),
                    eeml.Data('N5_Batt_V', battV,
                              unit=eeml.Unit('volts', 'basicSI', 'V'))])
        try:
          pac.put()
        except CosmError, e:
          print('ERROR: pac.put(): {}'.format(e))
        except StandardError:
          print('ERROR: StandardError')
        except:
          print('ERROR: Unexpected error: %s' % sys.exc_info()[0])

      else:
        rr = 0

  


# call the main() function
if __name__ == '__main__':
  main()
