#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

# http://www.danielsoper.com/statcalc3/calc.aspx?id=96
# https://www.mccallum-layton.co.uk/tools/statistic-calculators/confidence-interval-for-mean-calculator/#confidence-interval-for-mean-calculator

from results import RESULTS_BEST_IRIS, RESULTS_BEST_TTT, RESULTS_IRIS_TOURNAMENT, RESULTS_TTT_TOURNAMENT
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.mlab as mlab
import math

x = np.linspace(00.0,1.0,100)
patches = []
height = 6.0

#IRIS prop
# data = RESULTS_BEST_IRIS
# mean = np.mean(data)
# std = np.std(data)
# color = 'r'
# plt.plot(x,mlab.normpdf(x,mean,std),color)
# minv = 0.37
# maxv = 0.49
# plt.plot([minv, minv], [0.0, height], color)
# plt.plot([maxv, maxv], [0.0, height], color)
# patches.append(mpatches.Patch(color=color, label='Prop. Selection'))
# print("mean: "+str(mean)+", std: "+str(std))

# #IRIS tour
# data = RESULTS_IRIS_TOURNAMENT
# mean = np.mean(data)
# std = np.std(data)
# color = 'b'
# plt.plot(x,mlab.normpdf(x,mean,std),color)
# minv = 0.21
# maxv = 0.31
# plt.plot([minv, minv], [0.0, height], color)
# plt.plot([maxv, maxv], [0.0, height], color)
# patches.append(mpatches.Patch(color=color, label='Tournament'))
# print("mean: "+str(mean)+", std: "+str(std))

#TTT prop
data = RESULTS_BEST_TTT
mean = np.mean(data)
std = np.std(data)
color = 'r'
plt.plot(x,mlab.normpdf(x,mean,std),color)
minv = 0.52
maxv = 0.61
plt.plot([minv, minv], [0.0, height], color)
plt.plot([maxv, maxv], [0.0, height], color)
patches.append(mpatches.Patch(color=color, label='Prop. Selection'))
print("mean: "+str(mean)+", std: "+str(std))

#TTT our
data = RESULTS_TTT_TOURNAMENT
mean = np.mean(data)
std = np.std(data)
color = 'b'
plt.plot(x,mlab.normpdf(x,mean,std),color)
minv = 0.33
maxv = 0.41
plt.plot([minv, minv], [0.0, height], color)
plt.plot([maxv, maxv], [0.0, height], color)
patches.append(mpatches.Patch(color=color, label='Tournament'))
print("mean: "+str(mean)+", std: "+str(std))

plt.title("Normal Distribution for Results of Selector Op. (TTT Dataset)")
plt.legend(handles=patches)
plt.show()