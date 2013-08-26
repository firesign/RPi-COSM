#!/usr/bin/env python

from __future__ import division

import re #regular expressions
#import eeml
import serial
import os

fud = True
n1pointer = 0
n1temps = []

def main():
    
    
     
    while fud == True:
 
        def runningAverage(node, temperature, n1temps):
            if node == 1:
                global n1pointer
                total = 0
                
                # initially build-up the list of temperatures
                if len(n1temps) < 4:
                    n1temps.extend([temperature])
                    
                    for j in range(0, (n1pointer + 1)):
                        addend = float(n1temps[j])
                        total = float(addend + total)
                        avgx = total / (n1pointer + 1)
                # the list of temperatures is full, now replace the oldest one
                # with a new one
                else:
                    n1temps[n1pointer] = temperature
                    for j in range(0, 4):
                        addend = float(n1temps[j])
                        total = float(addend + total)
                        avgx = total / 4
                  
                average = round(avgx, 2)
                
                # increment  or reset pointer
                if n1pointer < 3:
                    n1pointer += 1

                else:
                    n1pointer = 0

            
                return (average, n1temps, n1pointer)    
            
        print "\nNEW TEMPERATURE READING *********************"

        temperature = raw_input("Input a temperature: ")
        temperature = float(temperature)
        average = runningAverage(1, temperature, n1temps)
        print "The average = %s C" % average[0]

# call the main() function
if __name__ == '__main__':
  main()