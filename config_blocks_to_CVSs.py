import struct
import csv
import os

# Definiuję sekwencję bajtów do wyszukania
search_bytes = bytes([0x03, 0x00, 0x02, 0x00])

with open('config.dat', 'rb') as f:
    data = f.read()

pos = data.find(search_bytes)

while pos != -1:
    print('found at address ', f'{pos:08X}', ' bytes with extra:', ' '.join(f'{b:02X}' for b in data[pos:pos+14]))
    adres = f'{pos:08X}'
    filename = f'{pos:08X}.csv'

    pos += len(search_bytes) + 3
    
    float_no = 0

    print('float is:                                                         ', ' '.join(f'{b:02X}' for b in data[pos:pos+4]))

    # Otwieram plik wyjściowy CSV

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter = ";")
        writer.writerow( ["block_address", "float_no", "value_little"])

        while data[pos:pos+4] != bytes([0, 0, 0, 0]):
            
            float_no += 1
            value = struct.unpack('f', data[pos:pos+4])[0]
            
            value_little = struct.unpack('<f', data[pos:pos+4])[0]
            # value_big    = struct.unpack('>f', data[pos:pos+4])[0] #nonsense

            writer.writerow( [ f'{adres}', f'{float_no}', f'{value_little:.28f}']) #for polish excel .replace('.', ',')

            pos += 4
        
    if float_no < 2:
        os.remove( filename )
    else:

        if os.path.isfile( f'{adres} ( {float_no} ).csv' ):
            os.remove( f'{adres} ( {float_no} ).csv' )

        os.rename(filename, f'{adres} ( {float_no} ).csv')
            

    print('last float and more:', ' '.join(f'{b:02X}' for b in data[pos-4:pos+64]))
    print('Data block saved to', f'{adres} ( {float_no} ).csv' )
    
    pos = data.find(search_bytes, pos)