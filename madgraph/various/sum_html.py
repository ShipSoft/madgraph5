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
from __future__ import division
import os
import math
import logging

logger = logging.getLogger('madevent.stdout') # -> stdout

pjoin = os.path.join


class OneResult(object):
    
    def __init__(self, name):
        """Initialize all data """
        
        self.name = name
        self.xsec = 0
        self.xerru = 0  # uncorrelated error
        self.xerrc = 0  # correlated error
        self.nevents = 0
        self.nw = 0     # Don't know
        self.maxit = 0  # 
        self.nunwgt = 0  # number of unweighted events
        self.luminosity = 0
        self.mfactor = 1 # number of times that this channel occur (due to symmetry)
        self.ysec_iter = []
        self.yerr_iter = []
        return
    
    def read_results(self, filepath):
        """read results.dat and fullfill information"""
        
        i=0
        for line in open(filepath):
            i+=1
            if i == 1:
                data = [float(d) for d in line.split()]
                self.xsec, self.xerru, self.xerrc, self.nevents, self.nw,\
                         self.maxit, self.nunwgt, self.luminosity = data
                if self.mfactor > 1:
                    self.luminosity /= self.mfactor
                    #self.ysec_iter.append(self.xsec)
                    #self.yerr_iter.append(0)
                continue
            try:
                l, sec, err, eff, maxwgt = line.split()
            except:
                return
            self.ysec_iter.append(float(sec))
            self.yerr_iter.append(float(err))
        
        
    def set_mfactor(self, value):
        self.mfactor = int(value)    
        
    def change_iterations_number(self, nb_iter):
        """Change the number of iterations for this process"""
            
        if len(self.ysec_iter) <= nb_iter:
            return
        
        # Combine the first iterations into a single bin
        nb_to_rm =  len(self.ysec_iter) - nb_iter
        ysec = [0]
        yerr = [0]
        for i in range(nb_to_rm):
            ysec[0] += self.ysec_iter[i]
            yerr[0] += self.yerr_iter[i]**2
        ysec[0] /= (nb_to_rm+1)
        yerr[0] = math.sqrt(yerr[0]) / (nb_to_rm + 1)
        
        for i in range(1, nb_iter):
            ysec[i] = self.ysec_iter[nb_to_rm + i]
            yerr[i] = self.yerr_iter[nb_to_rm + i]
        
        self.ysec_iter = ysec
        self.yerr_iter = yerr


class Combine_results(list, OneResult):
    
    def __init__(self, name):
        
        list.__init__(self)
        OneResult.__init__(self, name)
        output_path = None
    
    def add_results(self, name, filepath, mfactor=1):
        """read the data in the file"""
        oneresult = OneResult(name)
        oneresult.set_mfactor(mfactor)
        oneresult.read_results(filepath)
        self.append(oneresult)
    
    
    def compute_values(self):
        """compute the value associate to this combination"""

        self.compute_iterations()
        self.xsec = sum([one.xsec for one in self])
        self.xerrc = sum([one.xerrc for one in self])
        self.xerru = math.sqrt(sum([one.xerru**2 for one in self]))

        self.nevents = sum([one.nevents for one in self])
        self.nw = sum([one.nw for one in self])
        self.maxit = len(self.yerr_iter)  # 
        self.nunwgt = sum([one.nunwgt for one in self])  
        self.luminosity = min([one.luminosity for one in self])
    
    def compute_iterations(self):
        """Compute iterations to have a chi-square on the stability of the 
        integral"""

        nb_iter = min([len(a.ysec_iter) for a in self], 0)
        # syncronize all iterations to a single one
        for oneresult in self:
            oneresult.change_iterations_number(nb_iter)
            
        # compute value error for each iteration
        for i in range(nb_iter):
            value = [one.ysec_iter[i] for one in self]
            error = [one.yerr_iter[i]**2 for one in self]
            
            # store the value for the iteration
            self.ysec_iter.append(sum(value))
            self.yerr_iter.append(math.sqrt(sum(error)))
    
        
        
    template_file = \
"""
<head>
    <title>Process results</title>
    <script type="text/javascript" src="../sortable.js"></script>
    <link rel=stylesheet href="../mgstyle.css" type="text/css">
</head>
<body>
 <h2>Process results</h2> 
 <BR>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>s= %(cross)s &#177 %(error)s (%(unit)s)</b><br><br>
<table class="sortable" id='tablesort'>
<tr><th>Graph</th>
    <th> %(result_type)s</th>
    <th>Error</th>
    <th>Events (K)</th>
    <th>Unwgt</th>
    <th>Luminosity</th>
</tr>
%(table_lines)s
</table></body>
"""    
    table_line_template = \
"""
<tr><td align=right>%(P_title)s</td>
    <td align=right><a href=%(P_link)s> %(cross)s </a> </td>
    <td align=right>  %(error)s</td>
    <td align=right>  %(events)s</td>
    <td align=right>  %(unweighted)s</td>
    <td align=right>  %(luminosity)s</td>
</tr>
"""

    def write_html(self, output_path, run, unit):
        """write html output"""
        
        # store value for global cross-section
        P_grouping = {}

        self.output_path = output_path
        tables_line = ''
        for oneresult in self:
            if oneresult.name.startswith('P'):
                title = '<a href=../../SubProcesses/%(P)s/diagrams.html>%(P)s</a>' \
                                                          % {'P':oneresult.name}
                P = oneresult.name.split('_',1)[0]
                if P in P_grouping:
                    P_grouping[P] += float(oneresult.xsec)
                else:
                    P_grouping[P] = float(oneresult.xsec)
            else:
                title = oneresult.name
            
            if not isinstance(oneresult, Combine_results):
                link = '../../SubProcesses/%(P)s/%(G)s/%(R)s_log.txt' % \
                                        {'P': self.name,
                                         'G': oneresult.name,
                                         'R': run}
            else:
                link = os.path.relpath(oneresult.output_path, 
                                                   os.path.dirname(output_path))
            
            dico = {'P_title': title,
                    'P_link': link,
                    'cross': oneresult.xsec,
                    'error': oneresult.xerru,
                    'events': oneresult.nevents,
                    'unweighted': oneresult.nunwgt,
                    'luminosity': oneresult.luminosity
                   }
    
            tables_line += self.table_line_template % dico
        
        for P_name, cross in P_grouping.items():
            dico = {'P_title': '%s sum' % P_name,
                    'P_link': '',
                    'cross': cross,
                    'error': '',
                    'events': '',
                    'unweighted': '',
                    'luminosity': ''
                   }
            tables_line += self.table_line_template % dico

        dico = {'cross': self.xsec,
                'error': self.xerru,
                'unit': unit,
                'result_type': 'Cross-Section',
                'table_lines': tables_line
                }

        html_text = self.template_file % dico
        fsock = open(output_path, 'w')
        fsock.writelines(html_text)
    
    def write_results_dat(self, output_path):
        
        line = '%s %s %s %s %s %s %s %s \n' % (self.xsec, self.xerru, self.xerrc,
                 self.nevents, self.nw, self.maxit, self.nunwgt, self.luminosity)
        
        open(output_path,'w').writelines(line)



def make_all_html_results(cmd):
    """ """
    run = cmd.results.current['run_name']
    if not os.path.exists(pjoin(cmd.me_dir, 'HTML', run)):
        os.mkdir(pjoin(cmd.me_dir, 'HTML', run))
    
    unit = cmd.results.unit
            
    all = Combine_results(run)
    
    for Pdir in open(pjoin(cmd.me_dir, 'SubProcesses','subproc.mg')):
        Pdir = Pdir.strip()
        P_comb = Combine_results(Pdir)
        
        P_path = pjoin(cmd.me_dir, 'SubProcesses', Pdir)
        G_dir = [G for G in os.listdir(P_path) if G.startswith('G') and 
                                                os.path.isdir(pjoin(P_path,G))]
        
        for line in open(pjoin(P_path, 'symfact.dat')):
            name, mfactor = line.split()
            name = 'G' + name
            if float(mfactor) < 0:
                continue
            P_comb.add_results(name, pjoin(P_path,name,'results.dat'), mfactor)
        P_comb.compute_values()
        P_comb.write_html(pjoin(cmd.me_dir, 'HTML', run,'%s_results.html' % Pdir),
                          run, unit)
        P_comb.write_results_dat(pjoin(P_path, '%s_results.dat' % run))
        all.append(P_comb)
    all.compute_values()
    all.write_html(pjoin(cmd.me_dir, 'HTML', run, 'results.html'), run, unit)
    all.write_results_dat(pjoin(cmd.me_dir,'SubProcesses', 'results.dat'))
          
    return all.xsec, all.xerru
