################################################################################
#
# Copyright (c) 2011 The MadGraph Development team and Contributors
#
# This file is a part of the MadGraph 5 project, an application which 
# automatically generates Feynman diagrams and matrix elements for arbitrary
# high-energy processes in the Standard Model and beyond.
#
# It is subject to the MadGraph license which should accompany this 
# distribution.
#
# For more information, please visit: http://madgraph.phys.ucl.ac.be
#
################################################################################
"""A File for splitting"""

import sys
import re
import os

#dict
dico={'MGVersion':'old_version',
      'MGProcCard':'proc_card',
      'slha':'param_card',
      'MGRunCard':'run_card',
      'MWCard':'MadWeight_card',
      'TransferCard':'transfer_card'
      }

class banner:
    

    pat_begin=re.compile('<(?P<name>\w*)>')
    pat_end=re.compile('</(?P<name>\w*)>')

    def __init__(self,pos):

        self.pos=pos


    def split(self):
        self.file=open(self.pos,'r')

        for line in self.file:
            if self.pat_begin.search(line):
                self.write_card('./Cards/'+self.FindCardName(self.pat_begin.search(line).group('name')))


    def write_card(self,pos):

        print 'writing', pos
        ff=open(pos,'w')
        for line in self.file:
            if self.pat_end.search(line):
                ff.close()
                return
            else:
                ff.writelines(line)

    def FindCardName(self,tag):
        if tag in dico.keys():
            if '.' not in dico[tag]:
                return dico[tag]+'.dat'
            else:
                return dico[tag]
        else:
            import time
            out=tag.split('_',1)
            name=self.FindCardName(out[0])
            return name.split('.',1)[0]+'_'+out[1]+'.dat'

if __name__=='__main__':
    import MW_param
    MW_param.go_to_main_dir()
    opt=sys.argv
    print opt
    if len(opt)<2:
       name=raw_input('enter the run name to restore or the position of a banner file\n')
    else:
        name=opt[1]

    if ('/' not in name):
        ban=banner('./Events/'+name+'/'+name+'_banner.txt')
        pos='./Events/'+name+'/'
    else:
        ban=banner(name)
        pos='/'.join([part for part in name.split('/')[:-1]])
        
    ban.split()
    print 'done'
    
    if len(opt)==3:
        import_lhco=opt[2]
    else:
        import_lhco=raw_input('Do you want import the input.lhco file? (1/0)\n')

    
    if int(import_lhco):
        os.system('cp '+pos+'/input.lhco ./Events')
        print 'replace Events/input.lhco by '+pos+'/input.lhco'

