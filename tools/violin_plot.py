"""
Demo of the new violinplot functionality
http://matplotlib.org/examples/statistics/violinplot_demo.html
"""

import random
import numpy as np
import matplotlib.pyplot as plt

# fake data
fs = 10 # fontsize
pos = [1,2,3,4]
# data = [np.random.normal(size=100) for i in pos]
data = [
    [0.666, 0.579, 0.604, 0.567, 0.669, 0.41 , 0.465, 0.476, 0.56 , 0.542, 0.524, 0.612, 0.58 , 0.583, 0.657, 0.654, 0.65 , 0.56 , 0.542, 0.561, 0.583, 0.635, 0.57 , 0.456, 0.449],
    [0.65434, 0.65477, 0.56855, 0.55616, 0.50105, 0.65406, 0.65561, 0.62697, 0.65406, 0.65364, 0.65406, 0.6542, 0.5594, 0.567, 0.65449, 0.6542, 0.5575, 0.63217, 0.65477, 0.65449, 0.65948, 0.65449, 0.6542, 0.64942, 0.65477],
    [0.64329, 0.6542, 0.6542, 0.6542, 0.64308, 0.63569, 0.62528, 0.65815, 0.65589, 0.62141, 0.61289, 0.6585, 0.65716, 0.59895, 0.6333, 0.66033, 0.61303, 0.65385, 0.66624, 0.64259, 0.66441, 0.66624, 0.65519, 0.67088, 0.64259],
    [0.67145, 0.65561, 0.65505, 0.65498, 0.65491, 0.65639, 0.65723, 0.6542, 0.6542, 0.6542, 0.65625, 0.66188, 0.65822, 0.65519, 0.64104, 0.47529, 0.64245, 0.6535, 0.64189, 0.64034, 0.65434, 0.61486, 0.65174, 0.47529, 0.67307],
]

fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6,6))

# axes.violinplot(data, pos, points=20, widths=0.1,
#                       showmeans=True, showextrema=True, showmedians=True)
# axes.set_title('Custom violinplot 1', fontsize=fs)

# axes.violinplot(data, pos, points=40, widths=0.3,
#                       showmeans=True, showextrema=True, showmedians=True,
#                       bw_method='silverman')
# axes.set_title('Custom violinplot 2', fontsize=fs)

axes.violinplot(data, pos, points=60, widths=0.5, showmeans=True,
                      showextrema=True, showmedians=True, bw_method=0.5)
axes.set_title('Custom violinplot 3', fontsize=fs)

fig.suptitle("Violin Plotting Examples")
fig.subplots_adjust(hspace=0.4)
plt.show()


# # Violin Plots
# library(vioplot)
# x1 <- mtcars$mpg[mtcars$cyl==4]
# x2 <- mtcars$mpg[mtcars$cyl==6]
# x3 <- mtcars$mpg[mtcars$cyl==8]
# vioplot(x1, x2, x3, names=c("4 cyl", "6 cyl", "8 cyl"), 
#    col="gold")
# title("Violin Plots of Miles Per Gallon")