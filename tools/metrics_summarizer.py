import numpy

def round_value(value, round_decimals_to = 4):
    number = float(10**round_decimals_to)
    return int(value * number) / number

r = [

[39.79, 43.6, 36.4, 33.0, 34.0, 34.4, 38.0, 33.79, 29.6, 31.2, 27.0, 34.6, 28.8, 31.2],
[37.79, 47.4, 45.0, 35.0, 40.0, 39.2, 35.4, 29.2, 39.79, 25.4, 35.79, 36.0, 37.79, 33.79],
[38.0, 47.4, 40.2, 37.2, 34.0, 28.0, 43.0, 36.0, 31.8, 35.2, 30.6, 38.6, 30.8, 34.6],
[44.2, 44.4, 43.4, 33.0, 32.0, 36.6, 38.79, 33.2, 35.4, 31.6, 31.2, 35.4, 30.8, 29.0],
[42.0, 45.2, 35.4, 35.4, 37.6, 36.0, 38.2, 39.4, 36.4, 36.4, 32.2, 33.79, 38.6, 42.4],

]

s = []

for index, _ in enumerate(r[0]):
    temp = []
    for array in r:
        temp.append(array[index])
    s.append(round_value(numpy.mean(temp)))

print str(s)