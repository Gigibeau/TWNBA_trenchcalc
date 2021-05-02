from trenchcalc import Data

data = Data('50_RS_4_2.csv')

data.tilt_correction()
height, width = data.measure()
data.plot_3d()
print(height)
print(width)