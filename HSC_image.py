import os
import sys


def rename_HSC(path, SrcList):
    for file in os.listdir(path, SrcList):
        num = file.split('-')[0]
        fil = file.split('-')[3]
        os.rename(path + file, path + SrcList[int((int(num)-2)/5)][0]['SAMI_id'] + '_HSC-' + fil + '.fits')

def cutout_HSC(path, SrcList):
    cutout_str = ''
    cutout_str = cutout_str + '#? filter    ra       dec       sw     sh\n'
    for Src in SrcList:
        for fil in ['HSC-G','HSC-R','HSC-I','HSC-Z','HSC-Y']:
            cutout_str = cutout_str + '   %s  %sdeg  %sdeg  30asec  30asec\n'%(fil, Src[0]['RA'], Src[0]['DE'])
    file = open(output, 'w+')
    file.write(sqlstring)
    file.close()
    
def Help_info():
    print('Convert a catalog in csv format into table for HSC cutout, or rename the file for sami_viz usage.\n')
    print('    Usage:')
    print('    python HSC_image.py [*.csv] cutout [Output]')
    print('    python HSC_image.py [*.csv] rename [PATH]')
    print('    - input csv file must contain column of "RA" for right ascension and "DE" for declination')
if __name__ == '__main__':
    try:
        if len(sys.argv) >= 2:
            csv = sys.argv[0]
            mode = sys.argv[1]
        if len(sys.argv) >= 3:
            path = sys.argv[2]
        file = open(csv, 'r', encoding = 'UTF-8-sig')
        Catalog = file.readlines()
        file.close()
        Term = Catalog.pop(0).strip().split(',')
        SrcList = [[{},None, None] for i in range(len(Catalog))]
        SrcList_temp = []
        for i in range(len(Catalog)):
            SrcInfo = Catalog[i].strip().split(',')
            for j in range(len(Term)):
                SrcList[i][0][Term[j]] = SrcInfo[j]
        if mode == 'rename':
            rename_HSC(path, SrcList)
            print('Success!')
        if mode == 'cutout':
            cutout_HSC(SrcList)
    except:
        Help_info()