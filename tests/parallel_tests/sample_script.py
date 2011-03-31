#! /usr/bin/env python
################################################################################
#
# Copyright (c) 2009 The MadGraph Development team and Contributors
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

"""A sample script running a comparison between different ME generators using
objects and routines defined in me_comparator. To define your own test case, 
simply modify this script. Support for new ME generator is achieved through
inheritance of the MERunner class.
"""

import logging
import logging.config
import pydoc
import os
import sys

#Look for MG5/MG4 path
mg5_path = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-3])
print mg5_path
sys.path.append(mg5_path)

import me_comparator
from madgraph import MG4DIR
mg4_path = MG4DIR



if '__main__' == __name__: 
    # Get full logging info
    logging.config.fileConfig(os.path.join(mg5_path, 'tests', '.mg5_logging.conf'))
    logging.root.setLevel(logging.INFO)
    logging.getLogger('madgraph').setLevel(logging.INFO)
    logging.getLogger('cmdprint').setLevel(logging.INFO)
    logging.getLogger('tutorial').setLevel(logging.ERROR)
        
    logging.basicConfig(level=logging.INFO)
    #my_proc_list = ['u u~ > g y $ g', 'u~ u > g y $ g ', 'y > u u~','Z >  u u~']
    #my_proc_list = ['t t > t t', 't t~ > t t~', 't t~ > z z', 't z > t z', 't~ t~ > t~ t~', 't~ z > t~ z', 'g g > y y', 'g y > g y', 'y y > g g', 'y y > z z', 'y y > a a', 'y z > t t~', 'y z > y z', 'a y > a y',' z z > t t~', 'z z > y y', 'a a > y y']
    my_proc_list = ['t t~ > t t~','t t~ > y > t t~','t t~ > t t~ / y', 't t~ > t t~ / a z h g', 'y > t t~', 'y > t t~ g', 't t~ > t t~ / z h g','t t~ > t t~ / a h g','t t~ > t t~ / z a g', 't t~ > t t~ / h ', 't t~ > t t~ / z','t t~ > z > t t~']
    #my_proc_list += ['t t~ > z > t t~','u u~ > z > u u~', 't t~ > t t~', 'u u > u u']
    #my_proc_list = [ 't t~ > y > t t~','z z > y > t t~','t t~ > y > z z',' u u~ > y > t t~', 't t~ > y > u u~']
    #my_proc_list = [' t t~ > t t~ y', 't t~ > t t~ g','g g > g g g','u u~ > y > u u~', 't t~ > y > t t~' ]
    #my_proc_list = me_comparator.create_proc_list(['u', 'u~','t','t~','g','y','a'], initial=2,
    #                                              final=2)
    #my_proc_list = [p+' /z' for p in my_proc_list]

    #my_proc_list += me_comparator.create_proc_list(['u', 'u~','t','t~','g','y','z','a'], initial=1,
    #                                              final=2)
    #my_proc_list = me_comparator.create_proc_list_enhanced(
    #    ['u', 'u~', 'd', 'd~', 'g'],['six', 'six~'],['g'],
    #    initial=2, final_1=1, final_2 = 1)

    #my_proc_list += me_comparator.create_proc_list(['w+','w-','z','a','x1+','x1-','n1'], initial=2,
    #                                              final=3)
    #my_proc_list += me_comparator.create_proc_list(['g','u','u~','go','ul','ul~','ur','ur~'], initial=2,
    #                                              final=3)

    # Create a MERunner object for MG4
    my_mg4 = me_comparator.MG4Runner()
    my_mg4.setup(mg4_path)

    # Create a MERunner object for MG5
    my_mg5 = me_comparator.MG5Runner()
    my_mg5.setup(mg5_path, mg4_path)

    # Create a MERunner object for UFO-ALOHA-MG5
    my_mg5_ufo = me_comparator.MG5_UFO_Runner()
    my_mg5_ufo.setup(mg5_path, mg4_path)

    # Create a MERunner object for C++
    my_mg5_cpp = me_comparator.MG5_CPP_Runner()
    my_mg5_cpp.setup(mg5_path, mg4_path)

    # Create and setup a comparator
    my_comp = me_comparator.MEComparator()
    my_comp.set_me_runners(my_mg5_ufo, my_mg4)

    # Run the actual comparison
    my_comp.run_comparison(my_proc_list,
                           model=['RS_UFO_GF2','RS'],
                           orders={'QED':4, 'QCD':4, 'QTD':4}, energy=2000)

    # Do some cleanup
    #my_comp.cleanup()
    filename='mssm_results2.log'

    filename='mssm_results.log'

    # Print the output
    my_comp.output_result(filename=filename)

    pydoc.pager(file(filename,'r').read())

    # Print a list of non zero processes
    #print my_comp.get_non_zero_processes()

