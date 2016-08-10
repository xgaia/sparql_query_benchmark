#! /usr/bin/python3
"""
This script extract sample data from huge datasets
"""

import random, os, re

def purge(directory, pattern):
    """
    Remove files who match a pattern
    :directory: the directory to purge
    :patern: files with this pattern will be removed
    """
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))

purge('.', '_sample_')

ttl_dir = './'

files = ('Gene_Ath', 'GWAS_Ath')

for fil in files:
    print('processing '+fil+' ...')
    fp = open(ttl_dir+'/'+fil)
    lines = fp.readlines()
    header = lines[0]

    num_lines = sum(1 for line in open(ttl_dir+'/'+fil))

    print(fil+' contain '+str(num_lines)+' lines')

    for value in ('10', '100', '1000', '10000'):
        if int(value) > num_lines:
            print('file '+fil+' contain '+str(num_lines)+' lines, can\'t make a sample of '+value)
            break
        print('processing '+str(value)+' lines sample')
        random_lines = []

        filename = fil+'_sample_'+value
        fp_new = open(filename, 'a')
        fp_new.write(header)

        for x in range(0, int(value)):
            random_number = random.randint(2, num_lines)
            while random_number in random_lines:
                random_number = random.randint(2, num_lines)
            random_lines.append(random_number)
            fp_new.write(lines[random_number])
