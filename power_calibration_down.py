# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:41:43 2015

scanning aom and correct for the misalignment into fibre by adjusting rf power
"""

from CQTdevices import DDSComm, PowerMeterComm, WindFreakUsb2
import matplotlib.pylab as plt
import numpy as np
import time



# location of devices
Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO04-if00'

DDS_address = '/dev/ioboards/dds_QO0037'
DDS_channel = 0

#Connect to devices and create objects
pm = PowerMeterComm(Power_meter_address)

dds = DDSComm(DDS_address,DDS_channel)
pm.set_range(3)
#wind = WindFreakUsb2('/dev/serial/by-id/usb-Windfreak_Synth_Windfreak_CDC_Serial_014571-if00')


#Frequency range to scan in MHz
start = 139
stop = 211
step = 10

freq_range = np.arange(start,stop,step)
init_power=200
init_freq=180

initset_power=100

dds.set_power(initset_power)

max_power=800
def power_scan(freq_range,average=50,wavelength=780,target_power=0.01/1000,setpower_tolerance=0.001/1000,cf=False):
    pm = PowerMeterComm(Power_meter_address)
    dds = DDSComm(DDS_address,DDS_channel)
    pm.set_range(3)
    powers = []
    powers_adj=[]
    setpower=[]
    for i in range(len(freq_range)):
        dds.set_freq(freq_range[i])#set freq point
        #wind.set_freq(freq_range[i])
        value = []
        time.sleep(0.1)
        for m in range(average):
            power = pm.get_power(wavelength)
            value.append(power)
            time.sleep(5e-3) # delay between asking for next value
        p=np.mean(value)
        print('freq:',freq_range[i])
        print(p)
        powers.append(np.mean(value)) #average value to get more reliable number
        t=1
        ps=initset_power
        num_turn=0
        if cf==True:
            while( (p<(target_power-setpower_tolerance)) or (p>(target_power+setpower_tolerance)) ):
                sign=0
                if p>target_power:
                    sign=-1
                else:
                    sign=1
                t=abs(p-target_power)*1e5
                print('freq:',freq_range[i])
                print('delp:',str(p-target_power))
                print('tstep:',t)
                ps=ps+sign*t
                print('powerset:',ps)
                dds.set_power(int(ps))
                value=[]
                for m in range(average):
                    power = pm.get_power(wavelength)
                    value.append(power)
                    time.sleep(5e-3) # delay between asking for next value
                p=np.mean(value)
                print(p)
                num_turn=num_turn+1
                if ((ps>max_power) or (ps<0) or (num_turn>100)):
                    break
            setpower.append(int(ps))
            value=[]
            for m in range(average):
                power = pm.get_power(wavelength)
                value.append(power)
                time.sleep(5e-3) # delay between asking for next value
            powers_adj.append(np.mean(value))
    dds.set_power(init_power)
    dds.set_freq(init_freq)
    return (np.array(powers_adj)*1000.0,np.array(powers)*1000,setpower) # Coonvert to mW

dds.set_freq(init_freq)
dds.set_power(init_power)


#Calibration procedure
if __name__=="__main__":
    pm.set_range(3) # set suitable range for optical power being measured
    
    # set starting power make it low to ensure have enough adjustment when far from AOM resonance
    re=power_scan(freq_range,cf=True)
    powers_adj=[]
    powers = re[1]#run scan should take about a minute with 10 averages
    powers_adj = re[0]
    setpower= re[2]
    plt.plot(freq_range,powers,'-o')#plot data to make sure it makes sense
    plt.plot(freq_range,powers_adj,'-o',color='red')#plot data to make sure it makes sense
    
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power (mW)')
    plt.show()
    fig2=plt.figure()
    plt.plot(freq_range,setpower,'-o',color='black')#plot data to make sure it makes sense1
    plt.show()
    data = np.column_stack((freq_range,setpower,powers,powers_adj))
    np.savetxt('test.txt',data)
    
    
        


