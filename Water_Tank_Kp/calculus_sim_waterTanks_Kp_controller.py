'''
LICENSE AGREEMENT
In relation to this Python file:
1. Copyright of this Python file is owned by the author: Mark Misin
2. This Python code can be freely used and distributed
3. The copyright label in this Python file such as
copyright=ax_main.text(x,y,'© Mark Misin Engineering',size=z)
that indicate that the Copyright is owned by Mark Misin MUST NOT be removed.

WARRANTY DISCLAIMER!
This Python file comes with absolutely NO WARRANTY! 
In no event can the author of this Python file be held responsible
for whatever happens in relation to this Python file.
For example, if there is a bug in the code and because of that a project,
invention, or whatever it is used for fails - the author is NOT RESPONSIBLE!
'''

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import numpy as np

radius=5 # Radius of the tank - The tank is round.
bottom=0 # Initial volume of the tank
final_volume=100 # Final volume of the tank
dVol=10 # The change of volume on the vertical scale.
width_ratio=1 #Necessary for the horizontal axis
dt=0.04 # Time interval
t0=0 # Initial time of the simulation
t_end=50 # Final time of the simulation
frame_amount=int(t_end/dt) # Frame amount of the simulation
t=np.arange(t0,t_end+dt,dt) # Time vector
density_water=1000  # [kg/m^3]

Kp1=1000 # Proportional constant for the 1st tank

vol_o1_i=30 # Initial volume of the 1st tank
vol_r1_i=70 # Initial reference volume of the 1st tank

# 1st tank
vol_r1=np.zeros(len(t)) # 0 vector for storing reference volume values
vol_r1[0]=vol_r1_i
volume_Tank1=np.zeros(len(t)) # 0 vector for true volume values
volume_Tank1[0]=vol_o1_i # Insert the initial true volume as the initial element of the vector
error1=np.zeros(len(t)) # Create a 0 vector to store errors in the simulation
m_dot1=Kp1*error1 # Compute a 0 vector to store massflow control inputs
print(len(t))
# Start the simulation
for i in range(1,len(t)): # Iterate throughout the simulation (i goes from 1 till the length of the time vector, last element not counted, if len(t)=1251, then you go till 1250)
    if i<300:
    	# Determine reference value vector for tank 1 for this region, if i is less than 300
        vol_r1[i]=vol_r1_i
    elif i<600:
    	# Determine reference value vector for tank 1 for this region, if i is less than 600, but greater than 300
        vol_r1[i]=20
    elif i<900:
    	# Determine reference value vector for tank 1 for this region, if i is less than 900
        vol_r1[i]=90
    else:
    	# Determine reference value vector for tank 1 for this region, if i is greater or equal than 900
        vol_r1[i]=50

    # Compute the error between the reference value and the true value for tank 1
    error1[i-1]=vol_r1[i-1]-volume_Tank1[i-1]

    # Compute the control input for tank 1
    m_dot1[i]=Kp1*error1[i-1]

    # Compute the true tank volume in the next time step through this numerical integration (trapezoidal rule)
    volume_Tank1[i]=volume_Tank1[i-1]+(m_dot1[i-1]+m_dot1[i])/(2*density_water)*(dt)

# Start the animation
vol_r1_2=vol_r1


def update_plot(num):
    if num>=len(volume_Tank1):
        num=len(volume_Tank1)-1

    tank_12.set_data([0,0],[-63,volume_Tank1[num]-63])
    tnk_1.set_data(t[0:num],volume_Tank1[0:num])
    vol_r1.set_data([-radius*width_ratio,radius*width_ratio],[vol_r1_2[num],vol_r1_2[num]])
    vol_r1_line.set_data([t0,t_end],[vol_r1_2[num],vol_r1_2[num]])

    return vol_r1,tank_12,vol_r1_line,tnk_1,

# Set up your figure properties
fig=plt.figure(figsize=(16,9),dpi=120,facecolor=(0.8,0.8,0.8))
gs=gridspec.GridSpec(2,1)

# Create object for Tank1
ax0=fig.add_subplot(gs[0,:],facecolor=(0.9,0.9,0.9))
vol_r1,=ax0.plot([],[],'r',linewidth=2)
tank_12,=ax0.plot([],[],'royalblue',linewidth=260,zorder=0)
plt.xlim(-radius*width_ratio,radius*width_ratio)
plt.ylim(bottom,final_volume)
plt.xticks(np.arange(-radius,radius+1,radius))
plt.yticks(np.arange(bottom,final_volume+dVol,dVol))
plt.ylabel('tank volume [m^3]')
plt.title('Tank 1')
copyright=ax0.text(-radius*width_ratio,(final_volume+10)*3.2/3,'© Mark Misin Engineering',size=12)

# Create volume function
ax3=fig.add_subplot(gs[1,:], facecolor=(0.9,0.9,0.9))
vol_r1_line,=ax3.plot([],[],'r',linewidth=2,label='Reference')
tnk_1,=ax3.plot([],[],'blue',linewidth=4,label='Tank 1')
plt.xlim(0,t_end)
plt.ylim(0,final_volume)
plt.ylabel('tank volume [m^3]')
plt.xlabel('time [s]')
plt.grid(True)
plt.legend(loc='upper right',fontsize='small')

plane_ani=animation.FuncAnimation(fig,update_plot,
    frames=frame_amount,interval=20,repeat=True,blit=True)
plt.show()
