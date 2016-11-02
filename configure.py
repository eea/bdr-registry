#!/usr/bin/python
""" Configure settings.py based on environment variables
"""
import os
import shutil
BDR_REG_APP = os.environ.get('BDR_REG_APP', '/bdrreg/bdr-registry')

LOCALSETTINGS = os.environ.get('LOCALSETTINGS')


def main():
    ex_src = '/'.join([BDR_REG_APP, 'localsettings.py.example'])
    dst = '/'.join([BDR_REG_APP, 'bdr_registry', 'localsettings.py'])
    if LOCALSETTINGS:
        f = open(dst, 'w+')
        f.write(LOCALSETTINGS)
    else:
        shutil.copy(ex_src, dst)

if __name__ == "__main__":
    main()
