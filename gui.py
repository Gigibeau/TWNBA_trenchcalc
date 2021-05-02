from trenchcalc import Data

data = Data('50_RS_4_2.csv')

data.plot_3d()
data.tilt_correction()
data.plot_3d()
