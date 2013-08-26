#!/usr/bin/env python

from __future__ import division

import re #regular expressions
#import eeml
import serial
import os


def main():
    
  global n1pointer, n1temps, n2pointer, n2temps, n3pointer, n3temps
  n1pointer = 0
  n2pointer = 0
  n3pointer = 0
  n1temps = []
  n2temps = []
  n3temps = []
  
  fud = True

  while fud == True:
 
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
        
    #print "\nNEW TEMPERATURE READING *********************"
    node = raw_input("Input a node: ")

    if node == '1':
      pointer = n1pointer
      temps = n1temps

    elif node == '2':
      pointer = n2pointer
      temps = n2temps
      
    elif node == '3':
      pointer = n3pointer
      temps = n3temps
      
    temperature = raw_input("Input a temperature: ")
    temperature = float(temperature)
    average = runningAverage(node, temperature, pointer, temps)
    node = average[0]
    avrg = average[1]
    pointer = average[2]
    temps = average[3]
    print "The average = %s C" % average[1]
    
    print "Node: %s  Avg Temp: %s Celcius  Pointer: %s  List: %s" % (node, avrg, pointer, temps)
    
    if node == '1':
      n1pointer = pointer
      n1temps = temps
    elif node == '2':
      n2pointer = pointer
      n2temps = temps
    elif node == '3':
      n3pointer = pointer
      n3temps = temps

# call the main() function
if __name__ == '__main__':
  main()