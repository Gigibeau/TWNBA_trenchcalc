from trenchcalc import Data
from tkinter import *  # NOQA
from tkinter import filedialog

root = Tk()

var_tilt = IntVar()
var_3d_plot = IntVar()
var_save_plot = IntVar()
global file_list

button_open = Button(root, text="open", command=lambda: open_files())
button_open.grid(row=0, column=0)

checkbutton_tilt = Checkbutton(root, text='tilt correction?', variable=var_tilt)
checkbutton_tilt.grid(row=0, column=1)

checkbutton_3d_plot = Checkbutton(root, text='3d plot?', variable=var_3d_plot)
checkbutton_3d_plot.grid(row=0, column=2)

checkbutton_print_plot = Checkbutton(root, text='save plot?', variable=var_save_plot)
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
                                                  var_tilt,
                                                  var_3d_plot,
                                                  var_save_plot))
button_exec.grid(row=3, column=1)


def open_files():
    global file_list
    gathered_names = filedialog.askopenfilenames(title="Open File",
                                                 filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
                                                 )
    file_list = list(gathered_names)

    button_exec.config(state='normal')


def exec_measure(list_of_filenames, avg_level, corner_level, check_tilt, check_3d_plot, check_save_plot):
    for file in list_of_filenames:
        data = Data(file, avg_level, corner_level)
        if check_tilt:
            data.tilt_correction()
        if check_3d_plot:
            data.plot_3d()
        data.measure_chunks(check_save_plot)
        print(data.height)
        print(data.width)


root.mainloop()
