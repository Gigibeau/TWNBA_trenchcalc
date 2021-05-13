from trenchcalc import Data
from tkinter import *  # NOQA
from tkinter import filedialog
import pandas as pd

root = Tk()

var_tilt = IntVar()
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
entry_avg_level = Entry(root, width=2)
entry_avg_level.insert(END, 10)
entry_avg_level.grid(row=1, column=1)

label_corner_level = Label(root, text='corner level: ')
label_corner_level.grid(row=2, column=0)
entry_corner_level = Entry(root, width=2)
entry_corner_level.insert(END, 0.98)
entry_corner_level.grid(row=2, column=1)

button_exec = Button(root, text='Execute', state=DISABLED,
                     command=lambda: exec_measure(file_list,
                                                  int(entry_avg_level.get()),
                                                  float(entry_corner_level.get()),
                                                  var_tilt.get(),
                                                  var_3d_plot.get(),
                                                  var_save_plot.get()))
button_exec.grid(row=3, column=1)


def open_files():
    global file_list
    gathered_names = filedialog.askopenfilenames(title="Open File",
                                                 filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
                                                 )
    file_list = list(gathered_names)

    button_exec.config(state='normal')


def exec_measure(list_of_filenames, avg_level, corner_level, check_tilt, check_3d_plot, check_save_plot):
    output = pd.DataFrame(columns=['height', 'width', 'height_1', 'height_2', 'height_3', 'height_4', 'height_5',
                                   'height_6', 'height_7', 'height_8', 'height_9', 'width_1', 'width_2', 'width_3',
                                   'width_4', 'width_5', 'width_6', 'width_7', 'width_8', 'width_9'])

    for file in list_of_filenames:
        data = Data(file, avg_level, corner_level)

        if check_tilt:
            data.tilt_correction()

        if check_3d_plot:
            data.plot_3d()

        data.measure_chunks(check_save_plot)

        file_output = []
        file_output.extend([data.height, data.width])
        file_output.extend(data.chunks_heights)
        file_output.extend(data.chunks_widths)
        output.loc[data.file_name.split('/')[-1]] = file_output
    
    output.to_csv('summary.csv')


root.mainloop()
