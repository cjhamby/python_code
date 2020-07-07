# this file:
#    (1) grabs the weather data from an API
#    (2) parses it for pertinent information
#    (3) generates formatted data for the LED matrix display
#    (4) sends the data via i2c to the LED matrix controller

import requests
from smbus2 import SMBus


# weather divisions for each led
temperature_markers = [ 32,
                        38,
                        44,
                        50,
                        56,
                        62,
                        68,
                        74
]


# these addresses correspond to the teensy controller's code
teensy_addr = 0x0F

red_reg = [   0x50,
              0x51,
              0x52,
              0x53,
              0x54,
              0x55,
              0x56,
              0x57
]

blue_reg = [  0x70,
              0x71,
              0x72,
              0x73,
              0x74,
              0x75,
              0x76,
              0x77
]



colder_night = False       # does it get colder during the night?
num_hours = 8              # how many hours to get the forecast for?

# get the content from the weather site
forecast = requests.get('https://api.weather.gov/gridpoints/GSP/57,74/forecast/hourly')

# convert it from json into a python dictionary 
forecast = forecast.json()

# navigate through nested dictionaries to get to the forecast data
#
# uncomment to show the nested dictionaries
#          for x in forecast:
#          print(x)
forecast = forecast['properties']['periods']



# FORECAST contains like 100 hours worth of data
# we don't need that many hours
# so we create a new dict() and give it only a few hours' data
temp = dict()
for x in range(0,num_hours):
    temp[x] = forecast[x]

# if the forecast extends into nighttime,
# check to see if the night gets colder after 8hrs
# and if so, use that value for the last column
last_val = len(temp) - 1
check_val = last_val
while forecast[check_val]['isDaytime'] == False:
    check_val+=1
    # get the forecast for the next nighttime hour
    next_forecast = forecast[check_val]
    # is the next hour's temp the lowest so far?
    if (next_forecast['temperature'] < temp[last_val]['temperature']):
        temp[last_val] = next_forecast
        colder_night = True

# reassign the forecast variable to the new dict
forecast = temp;


# for x in forecast:
#     print(x)                 # show the nested dictionaries contained in FORECAST
#
# print(forecast[0].items())   # show the items in the dictionary
#
# the nested dictionaries are named numerically (0..7)
#
# relevant items:
#  temperature
#  shortForecast
#  windSpeed




# just to show what we're working with, we print it all out
print("the forecast for the next few hours is: ");
for x in range(0,last_val):
    print(forecast[x]['temperature'] , 'and' , forecast[x]['shortForecast'] )

if (colder_night == True):
    print("Tonight will get down to" , forecast[last_val]['temperature'] , 'and' , forecast[last_val]['shortForecast'])
else:
    print(forecast[last_val]['temperature'] , 'and' , forecast[last_val]['shortForecast'] )





# each row of the LED matrix is represented as an 8-bit number
# the rows will "fill in" according to the temperature, instead of displaying the binary weather data
# although that's an...interesting idea?
# anyhow, each bit is assigned a corresponding temperature value
# the LED is lit if the forecasted temperature is greater than the assigned bit value
#
weather_to_led = list()
for i in range(0,num_hours):
    t_val = 0x00                                 # t_val is the formatted temperature data
    f_val = forecast[i]['temperature']           # f_val is the unformatted forecast data
    for j in range(0,8):
        if(f_val > temperature_markers[j]):      # add a dot when the forecast is above the marker
            t_val = t_val >> 1                           # right shift and add 1
            t_val = (0x80 + t_val)
    weather_to_led.append(t_val)


# lastly, send the data to the teensy
with SMBus(1) as bus:
    for i in range(0,num_hours):
        # check if it will rain
        # there is no "chance of rain" data, only a short text description of the forecast
        # so we check for rain-y words
        forecast_words = forecast[i]['shortForecast']
        if ("Rain" in forecast_words) or ("Shower" in forecast_words) or ("Storm" in forecast_words):
            bus.write_byte_data(teensy_addr, blue_reg[i], weather_to_led[i])
            bus.write_byte_data(teensy_addr, red_reg[i], 0x00)
        else:
            bus.write_byte_data(teensy_addr, red_reg[i], weather_to_led[i])
            bus.write_byte_data(teensy_addr, blue_reg[i], 0x00)
