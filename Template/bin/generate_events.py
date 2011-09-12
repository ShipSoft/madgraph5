#! /usr/bin/env python
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
""" This is the main script in order to generate events in MadEvent """

import logging
import os
import re
import shutil
import subprocess
import sys
import time
root_path = os.path.split(os.path.dirname(os.path.realpath( __file__ )))[0]
pjoin = os.path.join
sys.path.append(pjoin(root_path,'bin','internal'))
import madevent_interface as ME        
################################################################################  
##   EXECUTABLE
################################################################################                                
if '__main__' == __name__:
    
    # Check that python version is valid
    if not (sys.version_info[0] == 2 or sys.version_info[1] > 5):
        sys.exit('MadEvent works with python 2.6 or higher (but not python 3.X).\n\
               Please upgrade your version of python.')
    
    # MadEvent is sensitive to the initial directory.
    # So go to the main directory
    os.chdir(root_path)
 
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.getLogger('madevent').setLevel(logging.INFO)
 
    argument = sys.argv
    try:
        mode = int(argument[1])
    except:
        mode = int(raw_input('Enter 2 for multi-core, 1 for parallel, 0 for serial run\n'))
    if mode == 0:
        try:
            name = argument[2]
        except:
            name = raw_input('Enter run name\n')
    else:
        try:
            opt = argument[2]
        except:
            if mode == 1: 
                opt = raw_input('Enter name for jobs on pbs queue\n')
            else:
                opt = int(raw_input('Enter number of cores\n'))
        
        try:
            name = argument[3]
        except:
            name = raw_input('enter run name\n')

    launch = ME.MadEventCmd(me_dir=os.getcwd())
        

    if mode == 1:
        launch.run_cmd('generate_events %s --cluster=%s --queue=%s'
                   %(name, mode, opt))            
        ME = MadEventLauncher(1, name=name, cluster_queue=opt)
    elif mode ==2:
        launch.run_cmd('generate_events %s --cluster=%s --nb_core=%s'
                   %(name, mode, opt)) 
    else:
        launch.run_cmd('generate_events %s' % name)
    
    launch.run_cmd('quit')
            
    # reconfigure path for the web 
    #if len(argument) == 5:
    #    ME.pass_in_web_mode()

             
        

        
    
    
    
    
    
    
    
