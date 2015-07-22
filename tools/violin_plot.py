"""
Demo of the new violinplot functionality
http://matplotlib.org/examples/statistics/violinplot_demo.html
"""

import random
import numpy as np
import matplotlib.pyplot as plt

# fake data
fs = 10 # fontsize
pos = [1,2,4,5,7,8]
data = [np.random.normal(size=100) for i in pos]

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