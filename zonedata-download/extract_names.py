'''
Reads zonefiles and only output registed domain names

for shell people :
    zcat date-zonefile.gz | cut -f 1 | uniq | sed 's/\.$//' > ouputfile


'''


from glob import glob
import gzip
import re
from collections import OrderedDict
import os
back = os.getcwd()

os.chdir('zonefiles')
zonefileglob = glob('*zone-data*gz')


def stripper(text):
    """ Gets fir colum of file
    >>> example = ('transportes.bradesco.	172800	in	ns	'
    ...            'ns1.bradesco.com.br.')
    >>> stripper(example)
    'transportes.bradesco'
    """
    return re.sub('\.\s.*', '', text)


if __name__ == '__main__':
    for zonefile in zonefileglob:
        print('Parsing: %s' % zonefile)

        with gzip.open(zonefile, 'rb') as gzfile:
            domainlist = stripper(gzfile.read().strip()).split('\n')
            uniquedomains = OrderedDict.fromkeys(domainlist)

        outputfile = zonefile.replace('zone-data.txt.gz', 'domainlist.txt')
        domains = uniquedomains.keys()[1:]  # First element is tld name
        with open(outputfile, 'wb') as outfile:
            outfile.write('\n'.join(domains))

    os.chdir(back)
