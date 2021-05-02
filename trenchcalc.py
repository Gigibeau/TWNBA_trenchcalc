import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm

# Loading in the csv file and cleaning it up
file_name = '50_RS_8_2.csv'
lext_data = pd.read_csv(file_name, error_bad_lines=False, skiprows=18)
lext_data.drop(lext_data.columns[-1], inplace=True, axis=1)
resolution = lext_data['DataLine']
lext_data.set_index('DataLine', inplace=True, drop=True)

for column in lext_data.columns:
    lext_data.rename(columns={column: int(column.split('= ')[1])}, inplace=True)
for column in lext_data.columns:
    lext_data.rename(columns={column: resolution[column - 1]}, inplace=True)

'''
X, Y = np.meshgrid(lext_data.columns, lext_data.index)
Z = lext_data

fig1 = plt.figure()
ax1 = fig1.add_subplot(1, 1, 1, projection='3d')
ax1.plot_surface(X, Y, Z, cmap=cm.viridis, rstride=5, cstride=5, linewidth=0)
ax1.azim = -10
plt.show()

fig2 = plt.figure()
lext_data['mean'] = lext_data.mean(axis=1)
ax2 = fig2.add_subplot(1, 1, 1)
sns.lineplot(data=lext_data, x=resolution, y='mean', ax=ax2)
plt.show()
'''

# Defining the limits
max_upper = lext_data.to_numpy().max()
min_lower = lext_data.to_numpy().min()
abs_range = max_upper - min_lower
max_lower = max_upper - (abs_range / 10)
min_upper = min_lower + (abs_range / 10)

# Correcting the tilt
tilt_corr_data = lext_data[(lext_data.mean(axis=1) > max_lower)]
mean_x = tilt_corr_data.mean(axis=1)
mean_y = tilt_corr_data.mean(axis=0)

slope_x, intercept_x = np.polyfit(tilt_corr_data.index, mean_x, 1)
abline_values_x = [slope_x * i + intercept_x for i in tilt_corr_data.index]

slope_y, intercept_y = np.polyfit(tilt_corr_data.columns, mean_y, 1)
abline_values_y = [slope_y * i + intercept_y for i in tilt_corr_data.columns]

x_map = []
for index in lext_data.index:
    x_map.append(slope_x * index)

y_map = []
for column in lext_data.columns:
    y_map.append(slope_y * column)

lext_data_corr = lext_data.copy()
#lext_data_corr = lext_data_corr.sub(y_map, axis=1)
#lext_data_corr = lext_data_corr.sub(x_map, axis=0)

mean_x_corr = lext_data_corr.mean(axis=1)
mean_y_corr = lext_data_corr.mean(axis=0)

# Plotting the effect of the tilt correction
corrected_x = []
counter = 0
for i in mean_x:
    corrected_x.append(i - (slope_x * tilt_corr_data.index[counter]))
    counter += 1

corrected_y = []
counter = 0
for i in mean_y:
    corrected_y.append(i - (slope_y * tilt_corr_data.columns[counter]))
    counter += 1

mean_x_2 = tilt_corr_data.mean(axis=1)
mean_y_2 = tilt_corr_data.mean(axis=0)

fig, ax = plt.subplots(1, 2, figsize=(10, 8))
sns.lineplot(x=tilt_corr_data.index, y=mean_x, ax=ax[0])
sns.lineplot(x=tilt_corr_data.index, y=abline_values_x, ax=ax[0])
sns.lineplot(x=lext_data_corr.index, y=mean_x_corr, ax=ax[0])

sns.lineplot(x=tilt_corr_data.columns, y=mean_y, ax=ax[1])
sns.lineplot(x=tilt_corr_data.columns, y=abline_values_y, ax=ax[1])
sns.lineplot(x=lext_data_corr.columns, y=mean_y_corr, ax=ax[1])

plt.show()

X, Y = np.meshgrid(lext_data_corr.columns, lext_data_corr.index)
Z = lext_data_corr

fig1 = plt.figure()
ax1 = fig1.add_subplot(1, 1, 1, projection='3d')
ax1.plot_surface(X, Y, Z, cmap=cm.viridis, rstride=5, cstride=5, linewidth=0)
ax1.azim = 90
ax1.elev = 5
plt.show()


X_2, Y_2 = np.meshgrid(lext_data.columns, lext_data.index)
Z_2 = lext_data

fig2 = plt.figure()
ax2 = fig2.add_subplot(1, 1, 1, projection='3d')
ax2.plot_surface(X_2, Y_2, Z_2, cmap=cm.viridis, rstride=5, cstride=5, linewidth=0)
ax2.azim = 90
ax2.elev = 5
plt.show()
