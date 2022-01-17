from time import sleep
from drive import RosAriaDriver

from math import sin, cos

robot=RosAriaDriver('/PIONIERX')
scan=robot.ReadLaser()

### read and write in json format
#import json
## print json to stdout
#print(json.dumps(scan))
##read data from file
#json_data = open('scan.json')
#data = json.load(json_data)

import matplotlib.pyplot as plt
import numpy as np

x = np.arange(0,512)
theta = (np.pi/512 )*x  # theta - scan angles in [rad]

fig1 = plt.figure()
#plotting in polar coordinates  
ax1 = fig1.add_axes([0.1,0.1,0.8,0.8],polar=True) 
line, = ax1.plot(theta,scan,'o',lw=2.5)
#setting range limits
ax1.set_ylim(0,5)  
plt.show()