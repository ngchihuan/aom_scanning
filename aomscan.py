# -*- coding: utf-8 -*-
"""
@author:nguyen chi huan
Scripts to scan aom freq and measure optical power changes.
main function: scanfreq
"""

#import timestampcontrol as tsc
from CQTdevices import DDSComm, PowerMeterComm
import matplotlib.pylab as plt
import time
import urllib3
import json
import numpy as np
Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO04-if00'
# location of devices
#DDS_address = '/dev/ioboards/dds_QO0037'
#DDS_channel = 1
pm = PowerMeterComm(Power_meter_address)

pm.set_range(3)
http = urllib3.PoolManager(num_pools=20)
url=http.request('GET',"http://192.168.101.76:8080/data")
#Connect to devices and create objects

#DDS = DDSComm(DDS_address,DDS_channel)

#Frequency range to scan in MHz
freq_point = 150

#Optical power from AOM in mW
power_set = 0.01

#cal_data = np.genfromtxt('power_calibrationup.txt')
wavelength=780
def scanfreq(cal_data,channel,DDS_address,fixamp=0):
    '''
    Scan aom frequency with either fix rf power or varied rf power stored in
    calibration table cal_data
    Frequency scanning range is stored in cal_data
    cal_data: exported from the power_calibration.py script
    cal_data[:,0]: frequency
    cal_data[:,1]: RF power
    
    COMMANDS:   scanfreq(cal_data,channel,fixamp=0)
    
                cal_data: calibration table
                channel: dds channel    
                DDS_address: DDS_address devices
                fixamp=0: use rf power from the calibration table
                fixamp!=0: use fixed rf power

    RETURNS:
                return(freq,amp,powers,freq_wmt)
                
                freq: nparray scanning frequency of aom
                amp: nparray scanning rf power of aom
                powers: powers measured on optical powermeter while scanning aom
                freq_wmt: freq measured by wavemeter
    '''
    dds = DDSComm(DDS_address,channel)
    freq=cal_data[:,0]
    if fixamp==0:
        amp=cal_data[:,1]
    else:
        amp=fixamp*np.ones(len(cal_data[:,0]))
    powers=[]#powers: powers measured on optical powermeter while scanning aom
    freq_wmt=[]#frequency measured wavemeter
    average=100
    for i in range(len(freq)):
        dds.set_freq(freq[i])#set freq point
        dds.set_power(int(amp[i]))
        #wind.set_freq(freq_range[i])
        value = []
        time.sleep(0.1)
        for m in range(average):
            power = pm.get_power(wavelength)
            value.append(power)
            time.sleep(1e-2) # delay between asking for next value
        p=np.mean(value)
        powers.append(p)
        
        
        url=http.request('GET',"http://wavemeter:8080/data")
        dat=json.loads(url.data.decode())
        
        re=float(dat['freq'].split()[0])*1e5
        freq_wmt.append(re)
    return(freq,amp,powers,freq_wmt)
if __name__=='__main__':
    re=scanfreq(cal_data)
    power=re[2]
    freq = re[0]
    freq_wmt=np.array(re[3])
    for i in range(len(freq_wmt)):
        if freq_wmt[i]<0:
            freq_wmt[i]=38422821
    freq_wmt=freq_wmt-38422821
    plt.plot(freq,power,'-o')#plot data to make sure it makes sense
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power (mW)')
    plt.show()