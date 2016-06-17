r = [40.356,45.6,40.08,34.72,35.5199,34.8399,38.678,34.318,34.598,31.96,31.358,35.678,33.3579,34.198]

sort = sorted(r, reverse=True)

s = []

for value in r:
    s.append(sort.index(value)+1)

print str(s)