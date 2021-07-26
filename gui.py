from trenchcalc import Data
from tkinter import *  # NOQA
from tkinter import filedialog
import pandas as pd
import numpy as np
import scipy
from scipy import stats


root = Tk()

var_tilt = IntVar(value=1)
var_3d_plot = IntVar()
var_save_plot = IntVar()
global file_list

button_open = Button(root, text="open", command=lambda: open_files())
button_open.grid(row=0, column=0)

checkbutton_tilt = Checkbutton(root, text='tilt correction', variable=var_tilt)
checkbutton_tilt.grid(row=0, column=1)

checkbutton_3d_plot = Checkbutton(root, text='3d plot', variable=var_3d_plot)
checkbutton_3d_plot.grid(row=0, column=2)

checkbutton_print_plot = Checkbutton(root, text='save plot', variable=var_save_plot)
checkbutton_print_plot.grid(row=0, column=3)

label_avg_level = Label(root, text='avg level: ')
label_avg_level.grid(row=1, column=0)
entry_avg_level = Entry(root, width=3)
entry_avg_level.insert(END, 5)
entry_avg_level.grid(row=1, column=1)

label_confidence_level = Label(root, text='confidence level: ')
label_confidence_level.grid(row=2, column=0)
entry_confidence_level = Entry(root, width=3)
entry_confidence_level.insert(END, 0.95)
entry_confidence_level.grid(row=2, column=1)

label_x = Label(root, text='x-value: ')
label_x.grid(row=3, column=0)
entry_x = Entry(root, width=3)
entry_x.insert(END, 100)
entry_x.grid(row=3, column=1)

button_exec = Button(root, text='Execute', state=DISABLED,
                     command=lambda: exec_measure(file_list,
                                                  int(entry_avg_level.get()),
                                                  float(entry_confidence_level.get()),
                                                  int(entry_x.get()),
                                                  var_tilt.get(),
                                                  var_3d_plot.get(),
                                                  var_save_plot.get()))
button_exec.grid(row=4, column=1)


def open_files():
    global file_list
    gathered_names = filedialog.askopenfilenames(title="Open File",
                                                 filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
                                                 )
    file_list = list(gathered_names)

    button_exec.config(state='normal')


def exec_measure(list_of_filenames, avg_level, confidence_level, x_value, check_tilt, check_3d_plot, check_save_plot):
    output = pd.DataFrame(columns=['height', 'width', 'etch_factor', 'confidence_etch_factors', 'confidence_level',
                                   'degrees_of_freedom', 'std_heights', 'std_widths', 'confidence_heights',
                                   'confidence_widths', 'height_1', 'height_2',
                                   'height_3', 'height_4', 'height_5', 'height_6', 'height_7', 'height_8', 'height_9',
                                   'height_10', 'height_11', 'height_12', 'height_13', 'height_14', 'height_15',
                                   'height_16', 'width_1', 'width_2', 'width_3', 'width_4', 'width_5', 'width_6',
                                   'width_7', 'width_8', 'width_9', 'width_10', 'width_11', 'width_12', 'width_13',
                                   'width_14', 'width_15', 'width_16', 'etch_factor_1', 'etch_factor_2',
                                   'etch_factor_3', 'etch_factor_4', 'etch_factor_5', 'etch_factor_6', 'etch_factor_7',
                                   'etch_factor_8', 'etch_factor_9', 'etch_factor_10', 'etch_factor_11',
                                   'etch_factor_12', 'etch_factor_13', 'etch_factor_14', 'etch_factor_15',
                                   'etch_factor_16', 'mean_heights', 'mean_widths', 'mean_etch_factors'])

    for file in list_of_filenames:
        data = Data(file, avg_level, confidence_level)

        if check_tilt:
            data.tilt_correction()

        if check_3d_plot:
            data.plot_3d()

        data.measure_chunks(check_save_plot)

        etch_factor = data.height / ((data.width - x_value) / 2)
        etch_factor_chunks = []
        for count in range(len(data.chunks_heights)):
            etch_factor_chunks.append(data.chunks_heights[count] / ((data.chunks_widths[count] - x_value) / 2))

        etch_factor_chunks_mean = np.mean(etch_factor_chunks)
        etch_factor_chunks_std_err = scipy.stats.sem(etch_factor_chunks)
        conf_calc_etch_factor_chunks = scipy.stats.t.interval(data.confidence_level, data.degrees_freedom,
                                                              etch_factor_chunks_mean, etch_factor_chunks_std_err)
        conf_etch_factor_chunks = abs(conf_calc_etch_factor_chunks[0] - conf_calc_etch_factor_chunks[1]) / 2

        file_output = []
        file_output.extend([data.height, data.width, etch_factor, conf_etch_factor_chunks, data.confidence_level,
                            data.degrees_freedom, data.heights_std, data.widths_std, data.conf_heights,
                            data.conf_widths])
        file_output.extend(data.chunks_heights)
        file_output.extend(data.chunks_widths)
        file_output.extend(etch_factor_chunks)
        file_output.append(data.chunks_heights_mean)
        file_output.append(data.chunks_widths_mean)
        file_output.append(sum(etch_factor_chunks) / len(etch_factor_chunks))
        output.loc[data.file_name.split('/')[-1]] = file_output
    
    output = output.T
    output_name = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
    output.to_csv(output_name)


root.mainloop()
