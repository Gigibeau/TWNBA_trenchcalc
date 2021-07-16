import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm
import scipy
from scipy import stats
import statistics


class Data:
    def __init__(self, file_name, avg_level, confidence_level):
        # Loading in the csv file and cleaning it up
        self.file_name = file_name.split('.')[0]
        self.lext_data = pd.read_csv(file_name, error_bad_lines=False, skiprows=18)
        self.lext_data.drop(self.lext_data.columns[-1], inplace=True, axis=1)
        self.resolution = self.lext_data['DataLine']
        self.lext_data.set_index('DataLine', inplace=True, drop=True)

        for column in self.lext_data.columns:
            self.lext_data.rename(columns={column: int(column.split('= ')[1])}, inplace=True)
        for column in self.lext_data.columns:
            self.lext_data.rename(columns={column: self.resolution[column]}, inplace=True)

        # Correcting spikes in the dataframe resulting from artifacts of the measurement
        self.mean = self.lext_data.mean(axis=1)
        self.mean_abs = self.lext_data.stack().mean()
        self.upper = self.mean[self.mean > self.mean_abs]
        self.upper_std = self.upper.std()
        self.upper_mean = self.upper.mean()
        #self.lower = self.mean[self.mean < self.mean_abs]
        #self.lower_std = self.lower.std()
        self.lext_data[self.lext_data > (self.upper_mean + 3 * self.upper_std)] = self.upper_mean + 3 * self.upper_std

        self.mean = self.lext_data.mean(axis=1)

        # Defining the limits
        self.max_upper = self.lext_data.values.max()
        self.min_lower = self.lext_data.values.min()
        self.abs_range = self.max_upper - self.min_lower
        self.avg_level = avg_level
        self.confidence_level = confidence_level
        self.max_lower = self.max_upper - (self.abs_range / self.avg_level)
        self.min_upper = self.min_lower + (self.abs_range / self.avg_level)
        self.max_avg = self.lext_data[(self.mean > self.max_lower)].mean().mean()

        # Defining the confidence and std
        self.degrees_freedom = 15

        # Defining output data
        self.height = 0
        self.width = 0
        self.chunks_heights = []
        self.chunks_widths = []

    def tilt_correction(self):
        # Correcting the tilt
        tilt_corr_data = self.lext_data[(self.lext_data.mean(axis=1) > self.max_lower)]
        mean_x = tilt_corr_data.mean(axis=1)
        mean_y = tilt_corr_data.mean(axis=0)

        slope_x, intercept_x = np.polyfit(tilt_corr_data.index, mean_x, 1)
        abline_values_x = [slope_x * i + intercept_x for i in tilt_corr_data.index]
        slope_y, intercept_y = np.polyfit(tilt_corr_data.columns, mean_y, 1)

        x_map = []
        for index in self.lext_data.index:
            x_map.append(slope_x * index)

        y_map = []
        for column in self.lext_data.columns:
            y_map.append(slope_y * column)

        lext_data_corr = self.lext_data.copy()
        lext_data_corr = lext_data_corr.sub(y_map, axis=1)
        lext_data_corr = lext_data_corr.sub(x_map, axis=0)

        mean_x_corr = lext_data_corr.mean(axis=1)

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        sns.lineplot(x=tilt_corr_data.index, y=mean_x, ax=ax)
        sns.lineplot(x=tilt_corr_data.index, y=abline_values_x, ax=ax)
        sns.lineplot(x=lext_data_corr.index, y=mean_x_corr, ax=ax)
        ax.set_ylim(bottom=self.max_lower)
        plt.show()

        self.lext_data = lext_data_corr
        self.mean = mean_x_corr
        self.max_avg = self.lext_data[(self.mean > self.max_lower)].mean().mean()

    def plot_3d(self):
        # Plotting 3D Plot
        x, y = np.meshgrid(self.lext_data.columns, self.lext_data.index)
        z = self.lext_data

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection='3d')
        ax.plot_surface(x, y, z, cmap=cm.viridis, rstride=5, cstride=5, linewidth=0)
        ax.azim = 20
        plt.savefig(self.file_name + '_3D')
        plt.show()

    def measure(self):
        # Measuring the trench
        right_corner = (self.mean.loc[self.mean.idxmin():] > (self.max_avg * self.confidence_level)).idxmax()
        left_corner = (self.mean.iloc[::-1].loc[self.mean.idxmin():] > (self.max_avg * self.confidence_level)).idxmax()

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        sns.lineplot(x=self.lext_data.index, y=self.mean, ax=ax)
        plt.axhline(y=self.mean.min(), color='red', alpha=0.5)
        plt.axhline(y=self.max_avg, color='red', alpha=0.5)
        plt.axvline(x=right_corner, color='red', alpha=0.5)
        plt.axvline(x=left_corner, color='red', alpha=0.5)
        plt.savefig(self.file_name)
        plt.show()
        height = (self.max_avg * self.confidence_level) - self.mean.min()
        width = right_corner - left_corner

        return height, width

    def measure_chunks(self, check_save):
        # Slicing the dataframe into 9 pieces and measuring the trenches of the individual slices
        right_corner_overall = (self.mean.loc[self.mean.idxmin():] > (self.max_avg * self.confidence_level)).idxmax()
        left_corner_overall = (
                self.mean.iloc[::-1].loc[self.mean.idxmin():] > (self.max_avg * self.confidence_level)).idxmax()

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        sns.lineplot(x=self.lext_data.index, y=self.mean, ax=ax)
        plt.axhline(y=self.mean.min(), color='red', alpha=0.5)
        plt.axhline(y=self.max_avg, color='red', alpha=0.5)
        plt.axvline(x=right_corner_overall, color='red', alpha=0.5)
        plt.axvline(x=left_corner_overall, color='red', alpha=0.5)
        if check_save:
            plt.savefig(self.file_name)

        plt.show()
        self.height = self.max_avg - self.mean.min()
        self.width = right_corner_overall - left_corner_overall

        chunk_size = int(self.lext_data.shape[1] / 16)

        for start in range(0, self.lext_data.shape[1], chunk_size):
            lext_data_subset = self.lext_data.iloc[:, start:start + chunk_size]
            mean = lext_data_subset.mean(axis=1)
            max_upper = lext_data_subset.values.max()
            min_lower = lext_data_subset.values.min()
            abs_range = max_upper - min_lower
            max_lower = max_upper - (abs_range / self.avg_level)
            max_avg = lext_data_subset[(mean > max_lower)].mean().mean()

            right_corner = (mean.loc[mean.idxmin():] > (max_avg * self.confidence_level)).idxmax()
            left_corner = (mean.iloc[::-1].loc[mean.idxmin():] > (max_avg * self.confidence_level)).idxmax()
            height = max_avg - mean.min()
            width = right_corner - left_corner
            self.chunks_heights.append(height)
            self.chunks_widths.append(width)


        self.chunks_heights_mean = np.mean(self.chunks_heights)
        self.chunks_widths_mean = np.mean(self.chunks_widths)
        self.heights_std_err = scipy.stats.sem(self.chunks_heights)
        self.widths_std_err = scipy.stats.sem(self.chunks_widths)
        self.heights_std = statistics.stdev(self.chunks_heights)
        self.widths_std = statistics.stdev(self.chunks_widths)
        self.conf_upper_heights = scipy.stats.t.interval(self.confidence_level, self.degrees_freedom,
                                                         self.chunks_heights_mean, self.heights_std_err)[0]
        self.conf_lower_heights = scipy.stats.t.interval(self.confidence_level, self.degrees_freedom,
                                                         self.chunks_heights_mean, self.heights_std_err)[1]
        self.conf_upper_widths = scipy.stats.t.interval(self.confidence_level, self.degrees_freedom,
                                                        self.chunks_widths_mean, self.widths_std_err)[0]
        self.conf_lower_widths = scipy.stats.t.interval(self.confidence_level, self.degrees_freedom,
                                                        self.chunks_widths_mean, self.widths_std_err)[1]

        self.conf_heights = abs(self.conf_lower_heights - self.conf_upper_heights) / 2
        self.conf_widths = abs(self.conf_lower_widths - self.conf_upper_widths) / 2
