import struct

import csv

import os

import pandas as pd

import matplotlib.pyplot as plt
import numpy as np

search_bytes = bytes([0x03, 0x00, 0x02, 0x00])

with open('config.dat', 'rb') as f:
    data = f.read()

    
swipes = pd.DataFrame(columns=['address_hex', 'address_dec', 'group', 'float_no', 'value_little'])

group = 1
data_found = 0

pos = data.find(search_bytes)

while pos != -1:

    adres = f'{pos:08X}'
    adres_dec = pos
    
    swipes_temp = pd.DataFrame(columns=['address_hex', 'address_dec', 'group', 'float_no', 'value_little'])
    
    # print('block header found at address ', f'{pos:08X}', ', bytes with extra:', ' '.join(f'{b:02X}' for b in data[pos:pos+14]))
    pos += len(search_bytes) + 3
    
    float_no = 0

    # print('float is:                                                                       ', ' '.join(f'{b:02X}' for b in data[pos:pos+4]))
    while data[pos:pos+4] != bytes([0, 0, 0, 0]) and data[pos:pos+4] != bytes([255, 255, 255, 255]):
            
        float_no += 1
 
        value_little = struct.unpack('<f', data[pos:pos+4])[0]

        swipes_temp.loc[ len( swipes_temp.index ) ] = [ "'"+adres+"'", adres_dec, group,  float_no, f'{value_little:.28f}' ] #for polish excel .replace('.', ',')

        pos += 4

    # print('last float and more:', ' '.join(f'{b:02X}' for b in data[pos-4:pos+64]))
    if float_no > 1:

        data_found = 1
       
        if len( swipes.index ) == 0: #first block
            swipes = swipes_temp
        else:
            swipes = pd.concat( [ swipes, swipes_temp ])
    else:
        if data_found != 0:
            group += 1
            data_found = 0

    pos = data.find(search_bytes, pos)

swipes.to_csv( "Groups  ( " + str( len( swipes ) ) +" ).dsv", index = False, sep=';' )

#graphs by groups found in file within proximity, and saved to files
groups = swipes['group'].unique()

for group in groups:

    addresses = swipes[swipes['group'] == group]['address_hex'].unique()

    nrows = int(np.ceil(len(addresses) / 3))
    print("GROUP =", group, "graphs =", len (addresses))

    fig, axs = plt.subplots(nrows=nrows, ncols=3, figsize=(15,5*nrows))

    for i, address in enumerate(addresses):
        # Wybierz tylko wiersze dla tego adresu
        df_address = swipes[swipes['address_hex'] == address]

        df_address.loc[:, 'value_little'] = pd.to_numeric(df_address['value_little'], errors='coerce')

        row = i // 3
        col = i % 3

        axs[row, col].plot(df_address['float_no'], df_address['value_little'])
        axs[row, col].set_title(f'ADDRESS {address}')
        axs[row, col].set_xlim([1, 200])

    for j in range(i+1, nrows*3):
        fig.delaxes(axs.flatten()[j])

    # Pokaż wykresy
    plt.tight_layout()
    plt.savefig(f'Group {group} graphs.png')
    plt.show()