#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

# http://www.danielsoper.com/statcalc3/calc.aspx?id=96
# https://www.mccallum-layton.co.uk/tools/statistic-calculators/confidence-interval-for-mean-calculator/#confidence-interval-for-mean-calculator

from results import *
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.mlab as mlab
import math

x = np.linspace(00.0,1.0,100)
patches = []
height = 6.0

data = [0.6302, 0.6302, 0.6302, 0.53382, 0.6302, 0.63, 0.43239, 0.6302, 0.6302, 0.62583, 0.19248, 0.21349, 0.61644, 0.63069, 0.6302, 
0.62047, 0.6302, 0.76527, 0.19463, 0.6302, 0.6302, 0.24494, 0.6302, 0.17463, 0.24363, 0.45271, 0.62544, 0.63709, 0.21183, 0.61691, 0.62569, 
0.6302, 0.6302, 0.51244, 0.61374, 0.6302, 0.32506, 0.48596, 0.62921, 0.6302]
mean = np.mean(data)
std = np.std(data)
color = 'r'
plt.plot(x,mlab.normpdf(x,mean,std),color)
minv = 0.5
maxv = 0.57
plt.plot([minv, minv], [0.0, height], color)
plt.plot([maxv, maxv], [0.0, height], color)
patches.append(mpatches.Patch(color=color, label='first policy'))
print("mean: "+str(mean)+", std: "+str(std))

data = [0.79305, 0.23421, 0.19094, 0.61169, 0.61624, 0.75325, 0.74278, 0.22723, 0.17731, 0.7265, 0.71353, 0.65909, 
0.72457, 0.60684, 0.78253, 0.23302, 0.77381, 0.86473, 0.77152, 0.76407, 0.78481, 0.68293, 0.81722, 0.51881, 0.74813, 0.68487, 0.78481, 0.19009, 0.78044, 
0.75711, 0.59277, 0.6302, 0.75057, 0.73512, 0.83318, 0.37733, 0.76775, 0.77985, 0.31087, 0.77624]
mean = np.mean(data)
std = np.std(data)
color = 'b'
plt.plot(x,mlab.normpdf(x,mean,std),color)
minv = 0.58
maxv = 0.68
plt.plot([minv, minv], [0.0, height], color)
plt.plot([maxv, maxv], [0.0, height], color)
patches.append(mpatches.Patch(color=color, label='second policy'))
print("mean: "+str(mean)+", std: "+str(std))

plt.title("Normal Distribution for Results of Sampling Policies")
plt.legend(handles=patches)
plt.show()