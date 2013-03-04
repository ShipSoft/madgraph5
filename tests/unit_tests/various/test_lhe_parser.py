################################################################################
#
# Copyright (c) 2012 The MadGraph Development team and Contributors
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
"""Test the validity of the LHE parser"""

import unittest
import madgraph.various.lhe_parser as lhe_parser


class TESTLHEParser(unittest.TestCase):


    def test_read_write_lhe(self):
        """test that we can read/write an lhe event file"""
        
        input= """<LesHouchesEvents version="1.0">
<header>
DATA
</header>
<init>
     2212     2212  0.70000000000E+04  0.70000000000E+04 0 0 10042 10042 3  1
  0.16531958660E+02  0.18860728290E+00  0.17208000000E+00   0
</init>
<event>
 4      0 +1.7208000e-01 1.00890300e+02 7.95774700e-02 1.27947900e-01
       -1 -1    0    0    0  501 +0.0000000e+00 +0.0000000e+00 +1.1943355e+01 1.19433546e+01 0.00000000e+00 0.0000e+00 1.0000e+00
        2 -1    0    0  501    0 +0.0000000e+00 +0.0000000e+00 -1.0679326e+03 1.06793262e+03 0.00000000e+00 0.0000e+00 -1.0000e+00
       24  1    1    2    0    0 +6.0417155e+00 +4.2744556e+01 -7.9238049e+02 7.97619997e+02 8.04190073e+01 3.4933e-25 -1.0000e+00
       23  1    1    2    0    0 -6.0417155e+00 -4.2744556e+01 -2.6360878e+02 2.82255979e+02 9.11880035e+01 1.8975e-26 1.0000e+00
</event>
<event>
 4      0 +1.7208000e-01 1.00890300e+02 7.95774700e-02 1.27947900e-01
       -1 -1    0    0    0  501 +0.0000000e+00 +0.0000000e+00 +1.1943355e+01 1.19433546e+01 0.00000000e+00 0.0000e+00 1.0000e+00
        2 -1    0    0  501    0 +0.0000000e+00 +0.0000000e+00 -1.0679326e+03 1.06793262e+03 0.00000000e+00 0.0000e+00 -1.0000e+00
       24  1    1    2    0    0 +6.0417155e+00 +4.2744556e+01 -7.9238049e+02 7.97619997e+02 8.04190073e+01 3.4933e-25 -1.0000e+00
       23  1    1    2    0    0 -6.0417155e+00 -4.2744556e+01 -2.6360878e+02 2.82255979e+02 9.11880035e+01 1.8975e-26 1.0000e+00
# balbalblb       
</event>            
<event>
  7     66 +1.5024446e-03 3.15138740e+02 7.95774720e-02 9.66701260e-02
       21 -1    0    0  502  501 +0.0000000e+00 +0.0000000e+00 -6.4150959e+01 6.41553430e+01 7.49996552e-01 0.0000e+00 0.0000e+00
        2 -1    0    0  501    0 +0.0000000e+00 +0.0000000e+00 +8.1067989e+02 8.10679950e+02 3.11899968e-01 0.0000e+00 0.0000e+00
       24  2    1    2    0    0 -1.5294533e+02 +1.0783429e+01 +4.5796553e+02 4.89600040e+02 8.04190039e+01 0.0000e+00 0.0000e+00
        2  1    3    3  503    0 -1.5351296e+02 +1.2743130e+01 +4.6093709e+02 4.85995489e+02 0.00000000e+00 0.0000e+00 0.0000e+00
       -1  1    3    3    0  503 +5.6763429e-01 -1.9597014e+00 -2.9715566e+00 3.60455091e+00 0.00000000e+00 0.0000e+00 0.0000e+00
       23  1    1    2    0    0 +4.4740095e+01 +3.2658177e+01 +4.6168760e+01 1.16254200e+02 9.11880036e+01 0.0000e+00 0.0000e+00
        1  1    1    2  502    0 +1.0820523e+02 -4.3441605e+01 +2.4239464e+02 2.68981060e+02 3.22945297e-01 0.0000e+00 0.0000e+00
# 2  5  2  2  1 0.11659994e+03 0.11659994e+03 8  0  0 0.10000000e+01 0.88172677e+00 0.11416728e+01 0.00000000e+00 0.00000000e+00
  <rwgt>
 0.25457988e+01 0.25457989e+01   3   0
 0.25457989e+01 0.26591987e+01 0.24350616e+01
 0.27825246e+01 0.29064692e+01 0.26614902e+01
 0.23467792e+01 0.24513140e+01 0.22446989e+01
  </rwgt>
</event>
</LesHouchesEvents> 
        
        """
        
        open('/tmp/event.lhe','w').write(input)
        
        input = lhe_parser.EventFile('/tmp/event.lhe')
        self.assertEqual(input.banner, """<LesHouchesEvents version="1.0">
<header>
DATA
</header>
<init>
     2212     2212  0.70000000000E+04  0.70000000000E+04 0 0 10042 10042 3  1
  0.16531958660E+02  0.18860728290E+00  0.17208000000E+00   0
</init>
""")
        
        nb_event = 0
        for event in input:
            nb_event +=1
            new = lhe_parser.Event(text=str(event))
            for part1,part2 in zip(event, new):
                self.assertEqual(part1, part2)
            self.assertEqual(new, event, '%s \n !=\n %s' % (new, event))
        self.assertEqual(nb_event, 3)
        
        
        
        