#!/usr/bin/python

# testing the temperature averaging function

#import sys

# Gather our code in a main() function
def main():
    t = 0.0
    temps = [0.0, 0.0, 0.0, 0.0]
    # first, add valid temps to fill list
    x = False
    while x == False:
        temps[0] = float(raw_input("Input a temperature: "))
        print temps
        avg = (temps[0])
        avg = round(avg, 2)
        print avg
        temps[1] = float(raw_input("Input a temperature: "))
        print temps
        avg = (temps[0] + temps[1]) / 2
        avg = round(avg, 2)
        print avg
        temps[2] = float(raw_input("Input a temperature: "))
        print temps
        avg = (temps[0] + temps[1] + temps[2]) / 3
        avg = round(avg, 2)
        print avg
        temps[3] = float(raw_input("Input a temperature: "))
        print temps
        avg = (temps[0] + temps[1] + temps[2] + temps[3]) / 4
        avg = round(avg, 2)
        print avg
        print temps
        print "End of first part\n"
        x = True
    while x:
        # steady state
        for i in range(0, 4):
            temps[i] = float(raw_input("Input a temperature: "))
            avg = (temps[0] + temps[1] + temps[2] + temps[3]) / 4
            avg = round(avg, 2)
            print avg
            print temps

if __name__ == '__main__':
    main()