import time
import datetime
import re
from crc import Calculator, Configuration, Crc16

"""
def calc_crc(buf):
    crc = 0xFFFF

    for d in buf:
        crc = (crc ^ d) & 0xffff

        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc = (crc ^ 0xA001) & 0xffff
            else:
                crc >>= 1
                crc &= 0xffff
     return crc
"""
modbus_crc = Calculator(Crc16.MODBUS, optimized=True)
                         
def calc_crc(buf):
    return modbus_crc.checksum(bytes(buf))

def wrap_phase_index(index):
    return index % 64

def wrap360(angle):
    return angle % 360.0

def phase_to_index(phase):
    n = int(round(phase/5.625)*5.625 / 5.625)
    return n

def db_to_str(db):
    if db >= 0.0:
        return '0'
    
    db = -31.5 if db < -31.5 else db

    db = round(db*2.0) / 2.0
    db_str = str(db).rstrip('0').rstrip('.')
    return db_str

def channel_to_index(chn:str):
    return int(chn[5]) - 1

def group_channel_name(row:int, col:int, polar:str=None):
    if polar is None:
        return group_channel_name(row, col, 'H') + group_channel_name(row, col, 'V')
    
    return ('G{}{}_A1{}'.format(row, col, polar), 
            'G{}{}_A2{}'.format(row, col, polar),
            'G{}{}_A3{}'.format(row, col, polar),
            'G{}{}_A4{}'.format(row, col, polar))

GROUP_CHANNEL_H = tuple((tuple(group_channel_name(j, i, 'H') for i in range(1, 9))) for j in range(1, 9))
GROUP_CHANNEL_V = tuple((tuple(group_channel_name(j, i, 'V') for i in range(1, 9))) for j in range(1, 9))
GROUP_CHANNEL = tuple((tuple(group_channel_name(j, i) for i in range(1, 9))) for j in range(1, 9))

CHUNKS = (
    (((1, 1), (1, 2), (2, 1), (2, 2)), ((1, 3), (1, 4), (2, 3), (2, 4)), ((1, 5), (1, 6), (2, 5), (2, 6)), ((1, 7), (1, 8), (2, 7), (2, 8))),  # Chunk11 - Chunk14
    (((3, 1), (3, 2), (4, 1), (4, 2)), ((3, 3), (3, 4), (4, 3), (4, 4)), ((3, 5), (3, 6), (4, 5), (4, 6)), ((3, 7), (3, 8), (4, 7), (4, 8))),  # Chunk21 - Chunk24
    (((5, 1), (5, 2), (6, 1), (6, 2)), ((5, 3), (5, 4), (6, 3), (6, 4)), ((5, 5), (5, 6), (6, 5), (6, 6)), ((5, 7), (5, 8), (6, 7), (6, 8))),  # Chunk31 - Chunk34
    (((7, 1), (7, 2), (8, 1), (8, 2)), ((7, 3), (7, 4), (8, 3), (8, 4)), ((7, 5), (7, 6), (8, 5), (8, 6)), ((7, 7), (7, 8), (8, 7), (8, 8)))   # Chunk41 - Chunk44
    )

def block_channel_name(block:tuple, polar:str):
    names = ()
    for bus in block:
        for group in bus['groups']:
            names += group_channel_name(int(group[0]), int(group[1]), polar)
    return names    

def block_to_name(b:tuple):
    if b == BLOCK1:
        return 'B1'
    if b == BLOCK2:
        return 'B2'
    if b == BLOCK3:
        return 'B3'
    if b == BLOCK4:
        return 'B4'
    raise ValueError('Invalid block')

#The groups are sorted by chip address
BLOCK1 = ({'bus':2, 'groups':((1, 4), (1, 3), (2, 4), (2, 3), (3, 4), (3, 3), (4, 4), (4, 3))}, {'bus':3, 'groups':((1, 2), (1, 1), (2, 2), (2, 1), (3, 2), (3, 1), (4, 2), (4, 1))})
BLOCK2 = ({'bus':0, 'groups':((1, 8), (1, 7), (2, 8), (2, 7), (3, 8), (3, 7), (4, 8), (4, 7))}, {'bus':1, 'groups':((1, 6), (1, 5), (2, 6), (2, 5), (3, 6), (3, 5), (4, 6), (4, 5))})
BLOCK3 = ({'bus':6, 'groups':((5, 4), (5, 3), (6, 4), (6, 3), (7, 4), (7, 3), (8, 4), (8, 3))}, {'bus':7, 'groups':((5, 2), (5, 1), (6, 2), (6, 1), (7, 2), (7, 1), (8, 2), (8, 1))})
BLOCK4 = ({'bus':4, 'groups':((5, 8), (5, 7), (6, 8), (6, 7), (7, 8), (7, 7), (8, 8), (8, 7))}, {'bus':5, 'groups':((5, 6), (5, 5), (6, 6), (6, 5), (7, 6), (7, 5), (8, 6), (8, 5))})

ALL_BLOCKS = (BLOCK1, BLOCK2, BLOCK3, BLOCK4)

BLOCK_CHANNEL_H = (block_channel_name(BLOCK1, 'H'), block_channel_name(BLOCK2, 'H'), block_channel_name(BLOCK3, 'H'), block_channel_name(BLOCK4, 'H'))
BLOCK_CHANNEL_V = (block_channel_name(BLOCK1, 'V'), block_channel_name(BLOCK2, 'V'), block_channel_name(BLOCK3, 'V'), block_channel_name(BLOCK4, 'V'))

def all_channel_name(polar):
    polar = polar.upper()
    names = ()

    if polar == 'HV' or polar == 'VH':
        for i in range(1, 9):
            for j in range(1, 9):
                names += group_channel_name(i, j, 'H')
        for i in range(1, 9):
            for j in range(1, 9):
                names += group_channel_name(i, j, 'V')        
               
    elif polar == 'H' or polar == 'V':
        for i in range(1, 9):
            for j in range(1, 9):
                names += group_channel_name(i, j, polar)
        
    return names     

ALL_CHANNEL_H = all_channel_name('H')
ALL_CHANNEL_V = all_channel_name('V')

def timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H_%M_%S')

def is_inverting_channel(name):
    if 'A2H' in name:
        return True
    if 'A3H' in name:
        return True
    if 'A3V' in name:
        return True
    if 'A4V' in name:
        return True
    
    return False

name_to_cartesian = {
    'G11_A1':(0, 0), 'G11_A2':(0, 1), 'G12_A1':(0, 2), 'G12_A2':(0, 3), 'G13_A1':(0, 4), 'G13_A2':(0, 5), 'G14_A1':(0, 6), 'G14_A2':(0, 7), 'G15_A1':(0, 8), 'G15_A2':(0, 9), 'G16_A1':(0, 10), 'G16_A2':(0, 11), 'G17_A1':(0, 12), 'G17_A2':(0, 13), 'G18_A1':(0, 14), 'G18_A2':(0, 15),
    'G11_A4':(1, 0), 'G11_A3':(1, 1), 'G12_A4':(1, 2), 'G12_A3':(1, 3), 'G13_A4':(1, 4), 'G13_A3':(1, 5), 'G14_A4':(1, 6), 'G14_A3':(1, 7), 'G15_A4':(1, 8), 'G15_A3':(1, 9), 'G16_A4':(1, 10), 'G16_A3':(1, 11), 'G17_A4':(1, 12), 'G17_A3':(1, 13), 'G18_A4':(1, 14), 'G18_A3':(1, 15),
    'G21_A1':(2, 0), 'G21_A2':(2, 1), 'G22_A1':(2, 2), 'G22_A2':(2, 3), 'G23_A1':(2, 4), 'G23_A2':(2, 5), 'G24_A1':(2, 6), 'G24_A2':(2, 7), 'G25_A1':(2, 8), 'G25_A2':(2, 9), 'G26_A1':(2, 10), 'G26_A2':(2, 11), 'G27_A1':(2, 12), 'G27_A2':(2, 13), 'G28_A1':(2, 14), 'G28_A2':(2, 15),
    'G21_A4':(3, 0), 'G21_A3':(3, 1), 'G22_A4':(3, 2), 'G22_A3':(3, 3), 'G23_A4':(3, 4), 'G23_A3':(3, 5), 'G24_A4':(3, 6), 'G24_A3':(3, 7), 'G25_A4':(3, 8), 'G25_A3':(3, 9), 'G26_A4':(3, 10), 'G26_A3':(3, 11), 'G27_A4':(3, 12), 'G27_A3':(3, 13), 'G28_A4':(3, 14), 'G28_A3':(3, 15),
    'G31_A1':(4, 0), 'G31_A2':(4, 1), 'G32_A1':(4, 2), 'G32_A2':(4, 3), 'G33_A1':(4, 4), 'G33_A2':(4, 5), 'G34_A1':(4, 6), 'G34_A2':(4, 7), 'G35_A1':(4, 8), 'G35_A2':(4, 9), 'G36_A1':(4, 10), 'G36_A2':(4, 11), 'G37_A1':(4, 12), 'G37_A2':(4, 13), 'G38_A1':(4, 14), 'G38_A2':(4, 15),
    'G31_A4':(5, 0), 'G31_A3':(5, 1), 'G32_A4':(5, 2), 'G32_A3':(5, 3), 'G33_A4':(5, 4), 'G33_A3':(5, 5), 'G34_A4':(5, 6), 'G34_A3':(5, 7), 'G35_A4':(5, 8), 'G35_A3':(5, 9), 'G36_A4':(5, 10), 'G36_A3':(5, 11), 'G37_A4':(5, 12), 'G37_A3':(5, 13), 'G38_A4':(5, 14), 'G38_A3':(5, 15),
    'G41_A1':(6, 0), 'G41_A2':(6, 1), 'G42_A1':(6, 2), 'G42_A2':(6, 3), 'G43_A1':(6, 4), 'G43_A2':(6, 5), 'G44_A1':(6, 6), 'G44_A2':(6, 7), 'G45_A1':(6, 8), 'G45_A2':(6, 9), 'G46_A1':(6, 10), 'G46_A2':(6, 11), 'G47_A1':(6, 12), 'G47_A2':(6, 13), 'G48_A1':(6, 14), 'G48_A2':(6, 15),
    'G41_A4':(7, 0), 'G41_A3':(7, 1), 'G42_A4':(7, 2), 'G42_A3':(7, 3), 'G43_A4':(7, 4), 'G43_A3':(7, 5), 'G44_A4':(7, 6), 'G44_A3':(7, 7), 'G45_A4':(7, 8), 'G45_A3':(7, 9), 'G46_A4':(7, 10), 'G46_A3':(7, 11), 'G47_A4':(7, 12), 'G47_A3':(7, 13), 'G48_A4':(7, 14), 'G48_A3':(7, 15),
    'G51_A1':(8, 0), 'G51_A2':(8, 1), 'G52_A1':(8, 2), 'G52_A2':(8, 3), 'G53_A1':(8, 4), 'G53_A2':(8, 5), 'G54_A1':(8, 6), 'G54_A2':(8, 7), 'G55_A1':(8, 8), 'G55_A2':(8, 9), 'G56_A1':(8, 10), 'G56_A2':(8, 11), 'G57_A1':(8, 12), 'G57_A2':(8, 13), 'G58_A1':(8, 14), 'G58_A2':(8, 15),
    'G51_A4':(9, 0), 'G51_A3':(9, 1), 'G52_A4':(9, 2), 'G52_A3':(9, 3), 'G53_A4':(9, 4), 'G53_A3':(9, 5), 'G54_A4':(9, 6), 'G54_A3':(9, 7), 'G55_A4':(9, 8), 'G55_A3':(9, 9), 'G56_A4':(9, 10), 'G56_A3':(9, 11), 'G57_A4':(9, 12), 'G57_A3':(9, 13), 'G58_A4':(9, 14), 'G58_A3':(9, 15),
    'G61_A1':(10, 0), 'G61_A2':(10, 1), 'G62_A1':(10, 2), 'G62_A2':(10, 3), 'G63_A1':(10, 4), 'G63_A2':(10, 5), 'G64_A1':(10, 6), 'G64_A2':(10, 7), 'G65_A1':(10, 8), 'G65_A2':(10, 9), 'G66_A1':(10, 10), 'G66_A2':(10, 11), 'G67_A1':(10, 12), 'G67_A2':(10, 13), 'G68_A1':(10, 14), 'G68_A2':(10, 15),
    'G61_A4':(11, 0), 'G61_A3':(11, 1), 'G62_A4':(11, 2), 'G62_A3':(11, 3), 'G63_A4':(11, 4), 'G63_A3':(11, 5), 'G64_A4':(11, 6), 'G64_A3':(11, 7), 'G65_A4':(11, 8), 'G65_A3':(11, 9), 'G66_A4':(11, 10), 'G66_A3':(11, 11), 'G67_A4':(11, 12), 'G67_A3':(11, 13), 'G68_A4':(11, 14), 'G68_A3':(11, 15),
    'G71_A1':(12, 0), 'G71_A2':(12, 1), 'G72_A1':(12, 2), 'G72_A2':(12, 3), 'G73_A1':(12, 4), 'G73_A2':(12, 5), 'G74_A1':(12, 6), 'G74_A2':(12, 7), 'G75_A1':(12, 8), 'G75_A2':(12, 9), 'G76_A1':(12, 10), 'G76_A2':(12, 11), 'G77_A1':(12, 12), 'G77_A2':(12, 13), 'G78_A1':(12, 14), 'G78_A2':(12, 15),
    'G71_A4':(13, 0), 'G71_A3':(13, 1), 'G72_A4':(13, 2), 'G72_A3':(13, 3), 'G73_A4':(13, 4), 'G73_A3':(13, 5), 'G74_A4':(13, 6), 'G74_A3':(13, 7), 'G75_A4':(13, 8), 'G75_A3':(13, 9), 'G76_A4':(13, 10), 'G76_A3':(13, 11), 'G77_A4':(13, 12), 'G77_A3':(13, 13), 'G78_A4':(13, 14), 'G78_A3':(13, 15),
    'G81_A1':(14, 0), 'G81_A2':(14, 1), 'G82_A1':(14, 2), 'G82_A2':(14, 3), 'G83_A1':(14, 4), 'G83_A2':(14, 5), 'G84_A1':(14, 6), 'G84_A2':(14, 7), 'G85_A1':(14, 8), 'G85_A2':(14, 9), 'G86_A1':(14, 10), 'G86_A2':(14, 11), 'G87_A1':(14, 12), 'G87_A2':(14, 13), 'G88_A1':(14, 14), 'G88_A2':(14, 15),
    'G81_A4':(15, 0), 'G81_A3':(15, 1), 'G82_A4':(15, 2), 'G82_A3':(15, 3), 'G83_A4':(15, 4), 'G83_A3':(15, 5), 'G84_A4':(15, 6), 'G84_A3':(15, 7), 'G85_A4':(15, 8), 'G85_A3':(15, 9), 'G86_A4':(15, 10), 'G86_A3':(15, 11), 'G87_A4':(15, 12), 'G87_A3':(15, 13), 'G88_A4':(15, 14), 'G88_A3':(15, 15),
}

cartesian_to_name = dict([(value, key) for key, value in name_to_cartesian.items()])

def to_cartesian(chn_name):
    return name_to_cartesian[chn_name[:-1]]

def to_name(row, col, polar):
    return cartesian_to_name[(row, col)] + polar.upper()
  