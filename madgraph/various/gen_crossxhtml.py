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
""" Create gen_crossxhtml """


import os
import pickle
try:
    import internal.files as files
    import internal.save_load_object as save_load_object
except:
    import madgraph.iolibs.files as files
    import madgraph.iolibs.save_load_object as save_load_object

pjoin = os.path.join
exists = os.path.exists

crossxhtml_template = """
<HTML> 
<HEAD> 
    <META HTTP-EQUIV="Refresh" CONTENT="10" > 
    <META HTTP-EQUIV="EXPIRES" CONTENT="20" > 
    <TITLE>Online Event Generation</TITLE>
</HEAD>
<BODY>
<script type="text/javascript">
function UrlExists(url) {
  var http = new XMLHttpRequest();
  http.open('HEAD', url, false);
  try{
     http.send()
     }
  catch(err){
   return 1==2;
  }
  return http.status!=404;
}
function check_link(url,alt, id){
    var obj = document.getElementById(id);
    if ( ! UrlExists(url)){
       obj.href = alt;
       return 1 == 2;
    }
    obj.href = url;
    return 1==1;
}
</script>    
    <H2 align=center> Results in the %(model)s for %(process)s </H2> 
    <HR>
    %(status)s
    <br>
    <br>
    <H2 align="center"> Available Results </H2>
        <TABLE BORDER=2 align="center" >  
            <TR align="center">
                <TH>Links</TH> 
                <TH>Output File</TH> 
                <TH NOWRAP> Tag </TH>
                <TH NOWRAP> Run </TH> 
                <TH>Collider</TH> 
                <TH> Cross section (pb) </TH> 
                <TH> Events  </TH> 
            </TR>     
            %(old_run)s
        </TABLE>
    <H3 align=center><A HREF="./index.html"> Main Page </A></H3>
</BODY> 
</HTML> 
"""

status_template = """
<H2 ALIGN=CENTER> Currently Running </H2>
<TABLE BORDER=2 ALIGN=CENTER>
    <TR ALIGN=CENTER>
        <TH nowrap ROWSPAN=2 font color="#0000FF"> Run Name </TH>
        <TH nowrap ROWSPAN=2 font color="#0000FF"> Cards </TH>   
        <TH nowrap ROWSPAN=2 font color="#0000FF"> Results </TH> 
        <TH nowrap ROWSPAN=1 COLSPAN=4 font color="#0000FF"> Status/Jobs
        <TR> 
            <TH>   Queued </TH>
            <TH>  Running </TH>
            <TH> Done  </TH>
            <TH> Total </TH>
        </TR>
    </TR>
    <TR ALIGN=CENTER> 
        <TD nowrap ROWSPAN=2> %(run_name)s </TD>
        <TD nowrap ROWSPAN=2> <a href="./Cards/param_card.dat">param_card</a><BR>
                    <a href="./Cards/run_card.dat">run_card</a><BR>
                    %(plot_card)s
                    %(pythia_card)s
                    %(pgs_card)s
                    %(delphes_card)s
                    
        </TD>
        <TD nowrap ROWSPAN=2> <A HREF="./SubProcesses/results.html">%(cross).4g <font face=symbol>&#177</font> %(error).4g (%(unit)s)</A> </TD> 
        %(status)s
 </TR></TABLE>
"""

class AllResults(dict):
    """Store the results for all the run of a given directory"""
    
    web = False 
    
    def __init__(self, model, process, path):
        
        dict.__init__(self)
        self.order = []
        self.process = ', '.join(process)
        if len(self.process) > 60:
            pos = self.process[50:].find(',')
            if pos != -1:
                self.process = self.process[:50+pos] + ', ...'
        self.path = path
        self.model = model
        self.status = ''
        self.current = None
    
    def def_current(self, name):
        """define the name of the current run"""
        assert name in self or name == None
        if name:
            self.current = self[name]
        else:
            self.current = None
    
    def delete_run(self, name):
        """delete a run from the database"""
        if self.current == name:
            self.results.def_current(None)                    
        del self[name]
        self.order.remove(name)
        #update the html
        self.output()
        
        
    
    def def_web_mode(self, web):
        """define if we are in web mode or not """
        if web is True:
            try:
                web = os.environ['SERVER_NAME']
            except:
                web = 'my_computer'
        self['web'] = web
        self.web = web
        
    def add_run(self, name, run_card, current=True):
        """ Adding a run to this directory"""
        
        new = OneRunResults(name, run_card, self.process, self.path)
        self[name] = new
        self.def_current(name)
        if name in self.order:
            self.order.remove(name)
        self.order.append(name)
        if current:
            self.def_current(name)
        
        
    def update(self, status, level, makehtml=True):
        """update the current run status"""
        if self.current:
            self.current.update_status(level)
        self.status = status
        if self.status:
            self.debug = None
        if makehtml:
            self.output()

    def resetall(self):
        """check the output status of all run"""
        
        for run in self.keys():
            if run == 'web':
                continue
            self.def_current(run)
            self.clean()
            self.current.update_status()

    def clean(self, levels = ['all']):
        """clean the run for the levels"""

        if not self.current:
            return
        to_clean = self.current
        run = to_clean['run_name']

        if 'all' in levels:
            levels = ['parton', 'pythia', 'pgs', 'delphes', 'channel']
        
        if 'parton' in levels:
            to_clean.parton = []
        if 'pythia' in levels:
            to_clean.pythia = []
        if 'pgs' in levels:
            to_clean.pgs = []
        if 'delphes' in levels:
            to_clean.delphes = []
        
        if run in self.order:
            self.order.remove(run)
        self.order.insert(0, run)
            
        
    def save(self):
        """Save the results of this directory in a pickle file"""
        filename = pjoin(self.path, 'HTML', 'results.pkl')
        save_load_object.save_to_file(filename, self)

    def add_detail(self, name, value, run=None):
        """ add information to current run (cross/error/event)"""
        
        assert name in ['cross', 'error', 'nb_event', 'cross_pythia']
        if not run:
            run = self.current
        else:
            run = self[run]
        
        if name == 'cross_pythia':
            run[name] = '<br> matched: %.4g' % float(value)
            run['nb_event_text'] = '%s <br> matched: %d' % (self.current['nb_event'],
                    int(self.current['nb_event']) * float(value) /float(self.current['cross'])) 
        elif name == 'nb_event':
            run[name] = value
            run['nb_event_text'] = value
        else:    
            run[name] = value
            if name == 'cross':
                self.current.results = True
        
    def output(self):
        """ write the output file """
        
        # 1) Create the text for the status directory        
        if self.status and self.current:
            if isinstance(self.status, str):
                status = '<td ROWSPAN=2 colspan=4>%s</td>' %  self.status
            else:
                s = self.status
                status ='''<td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td>
                </tr><tr><td colspan=4><center> %s </center></td>''' % (s[0],s[1], s[2], sum(s[:3]), s[3])
                
            
            status_dict = {'status': status,
                            'cross': self.current['cross'],
                            'error': self.current['error'],
                            'unit': self.current['unit'],
                            'run_name': self.current['run_name']}
            if exists(pjoin(self.path, 'Cards', 'plot_card.dat')):
                status_dict['plot_card'] = """ <a href="./Cards/plot_card.dat">plot_card</a><BR>"""
            else:
                status_dict['plot_card'] = ""
            if exists(pjoin(self.path, 'Cards', 'pythia_card.dat')):
                status_dict['pythia_card'] = """ <a href="./Cards/pythia_card.dat">pythia_card</a><BR>"""
            else:
                status_dict['pythia_card'] = ""
            if exists(pjoin(self.path, 'Cards', 'pgs_card.dat')):
                status_dict['pgs_card'] = """ <a href="./Cards/pgs_card.dat">pgs_card</a><BR>"""
            else:
                status_dict['pgs_card'] = ""
            if exists(pjoin(self.path, 'Cards', 'delphes_card.dat')):
                status_dict['delphes_card'] = """ <a href="./Cards/delphes_card.dat">delphes_card</a><BR>"""
            else:
                status_dict['delphes_card'] = ""
            
            status = status_template % status_dict
        else:
            status =''
        
        
        # See if we need to incorporate the button for submission
        if os.path.exists(pjoin(self.path, 'RunWeb')):       
           running  = True
        else:
            running = False
        
        # 2) Create the text for the old run:
        old_run = ''
        for key in self.order:
            old_run += self[key].info_html(self.path, self.web, running)
        
        text_dict = {'process': self.process,
                     'model': self.model,
                     'status': status,
                     'old_run': old_run}
        
        text = crossxhtml_template % text_dict
        open(pjoin(self.path,'crossx.html'),'w').write(text)
        
        
class OneRunResults(dict):
    """ Store the results of a specific run """
    
    def __init__(self, run_name, run_card, process, path):
        """initialize the object"""
        
        # define at run_result
        self['run_name'] = run_name
        self['tag'] = run_card['run_tag']
        self.event_path = pjoin(path,'Events')
        self.me_dir = path
        self.debug = None
        
        # Set the collider information
        data = process.split('>',1)[0].split()
        if len(data) == 2:
            name1,name2 = data
            if run_card['lpp1'] == '-1':
                name1 += '~'
            elif run_card['lpp1'] == '2':
                name1 = ' a'
            if run_card['lpp2'] == '-1':
                name2 += '~'
            elif run_card['lpp2'] == '2':
                name2 = ' a'                
            self['collider'] = '''%s %s <br> %s x %s  GeV''' % \
                    (name1, name2, run_card['ebeam1'], run_card['ebeam2'])
            self['unit'] = 'pb'                       
        else:
            self['collider'] = 'decay'
            self['unit'] = 'GeV'
        
        # Default value
        self['nb_event'] = None
        self['nb_event_text'] = 'No events yet'
        self['cross'] = 0
        self['cross_pythia'] = ''
        self['error'] = 0
        self.parton = [] 
        self.pythia = []
        self.pgs = []
        self.delphes = []
        self.results = False #no results.html 
        
        # data 
        self.status = ''
        
    def update_status(self, level='all'):
        """update the status of the current run """

        exists = os.path.exists
        run = self['run_name']
        path = self.event_path
        # Check if the output of the last status exists
        
        if level in ['gridpack','all']:
            if 'gridpack' not in self.parton and \
                    exists(pjoin(path, os.pardir,"%s_gridpack.tar.gz" % run)):
                self.parton.append('gridpack')
        
        if level in ['parton','all']:
            
            if 'lhe' not in self.parton and \
                        (exists(pjoin(path,"%s_unweighted_events.lhe.gz" % run)) or
                         exists(pjoin(path,"%s_unweighted_events.lhe" % run))):
                self.parton.append('lhe')
        
            if 'root' not in self.parton and \
                          exists(pjoin(path,"%s_unweighted_events.root" % run)):
                self.parton.append('root')
            
            if 'plot' not in self.parton and \
                                      exists(pjoin(path,"%s_plots.html" % run)):
                self.parton.append('plot')

        if level in ['pythia', 'all']:
            
            if 'plot' not in self.pythia and \
                               exists(pjoin(path,"%s_plots_pythia.html" % run)):
                self.pythia.append('plot')
            
            if 'lhe' not in self.pythia and \
                            (exists(pjoin(path,"%s_pythia_events.lhe.gz" % run)) or
                             exists(pjoin(path,"%s_pythia_events.lhe" % run))):
                self.pythia.append('lhe')

            if 'hep' not in self.pythia and \
                            (exists(pjoin(path,"%s_pythia_events.hep.gz" % run)) or
                             exists(pjoin(path,"%s_pythia_events.hep" % run))):
                self.pythia.append('hep')
            
            if 'root' not in self.pythia and \
                              exists(pjoin(path,"%s_pythia_events.root" % run)):
                self.pythia.append('root')
                
            if 'lheroot' not in self.pythia and \
                          exists(pjoin(path,"%s_pythia_lhe_events.root" % run)):
                self.pythia.append('lheroot')
            
            if 'log' not in self.pythia and \
                          exists(pjoin(path,"%s_pythia.log" % run)):
                self.pythia.append('log')     

        if level in ['pgs', 'all']:
            
            if 'plot' not in self.pgs and \
                         exists(pjoin(path,"%s_plots_pgs.html" % run)):
                self.pgs.append('plot')
            
            if 'lhco' not in self.pgs and \
                              (exists(pjoin(path,"%s_pgs_events.lhco.gz" % run)) or
                              exists(pjoin(path,"%s_pgs_events.lhco." % run))):
                self.pgs.append('lhco')
                
            if 'root' not in self.pgs and \
                                 exists(pjoin(path,"%s_pgs_events.root" % run)):
                self.pgs.append('root')
            
            if 'log' not in self.pgs and \
                          exists(pjoin(path,"%s_pgs.log" % run)):
                self.pgs.append('log') 
    
        if level in ['delphes', 'all']:
            
            if 'plot' not in self.delphes and \
                              exists(pjoin(path,"%s_plots_delphes.html" % run)):
                self.delphes.append('plot')
            
            if 'lhco' not in self.delphes and \
                 (exists(pjoin(path,"%s_delphes_events.lhco.gz" % run)) or
                 exists(pjoin(path,"%s_delphes_events.lhco" % run))):
                self.delphes.append('lhco')
                
            if 'root' not in self.delphes and \
                             exists(pjoin(path,"%s_delphes_events.root" % run)):
                self.delphes.append('root')     
            
            if 'log' not in self.delphes and \
                          exists(pjoin(path,"%s_delphes.log" % run)):
                self.delphes.append('log') 
        

    def info_html(self, path, web=False, running=False):
        """ Return the line of the table containing run info for this run """

        if not running:
            self['web'] = web
            self['me_dir'] = path
            
        out = "<tr>"
        # Links Events Tag Run Collider Cross Events
        
        #Links:
        out += '<td>'
        
            
            
        out += """<a href="./Events/%(run_name)s_banner.txt">banner</a>"""
        if web:
            out += """<br><a href="./%(run_name)s.log">log</a>"""
        if self.debug:
            out += """<br><a href="./%(run_name)s_debug.log"><font color=red>ERROR DETECTED</font></a>"""
        out += '</td>'
        # Events
        out += '<td>'
        out += self.get_html_event_info(web, running)
        out += '</td>'
        # Tag
        out += '<td> %(tag)s </td>'
        # Run
        out += '<td> %(run_name)s </td>'
        # Collider
        out += '<td> %(collider)s </td>'
        # Cross
        out += '<td><center>'
        if self.results:
                out += """<a href="./SubProcesses/%(run_name)s_results.html">"""
        out += '%(cross).4g <font face=symbol>&#177</font> %(error).2g %(cross_pythia)s'
        if self.results:
            out += '</a>'
        out+='</center></td>'
        # Events
        out += '<td> %(nb_event_text)s </td>' 

        return out % self
    
    def special_link(self, link, level, name):
        
        id = '%s_%s_%s' % (self['run_name'], level, name)
        
        return " <a  id='%(id)s' href='%(link)s' onClick=\"check_link('%(link)s.gz','%(link)s','%(id)s')\">%(name)s</a>" \
              % {'link': link, 'id': id, 'name':name}
    
    def get_html_event_info(self, web=False, running=False):
        """return the events information"""
        
        # Events
        out = '<table border=1>'
        if 'gridpack' in self.parton:
            out += '<tr><td> GridPack : </td><td>'
            out += self.special_link("./%(run_name)s_gridpack.tar",
                                                                 'gridpack', 'gridpack')
            out += "</td></tr>"

        if self.parton and self.parton != ['gridpack']:
            
            out += '<tr><td> Parton Events : </td><td>'
            
            if 'lhe' in self.parton:
                link = './Events/%(run_name)s_unweighted_events.lhe'
                level = 'parton'
                name = 'LHE'
                out += self.special_link(link, level, name) 
            if 'root' in self.parton:
                out += ' <a href="./Events/%(run_name)s_unweighted_events.root">rootfile</a>'
            if 'plot' in self.parton:
                out += ' <a href="./Events/%(run_name)s_plots.html">plots</a>'
            out += '</td></tr>'
        if self.pythia:
            out += '<tr><td> Pythia Events : </td><td>'
            
            if 'log' in self.pythia:
                out += """ <a href="./Events/%(run_name)s_pythia.log">LOG</a>"""
            if 'hep' in self.pythia:
                link = './Events/%(run_name)s_pythia_events.hep'
                level = 'pythia'
                name = 'STDHEP'
                out += self.special_link(link, level, name)                 
            if 'lhe' in self.pythia:
                link = './Events/%(run_name)s_pythia_events.lhe'
                level = 'pythia'
                name = 'LHE'                
                out += self.special_link(link, level, name) 
            if 'root' in self.pythia:
                out += """ <a href="./Events/%(run_name)s_pythia_events.root">rootfile (LHE)</a>"""
            if 'lheroot' in self.pythia:
                out += """ <a href="./Events/%(run_name)s_pythia_lhe_events.root">rootfile (LHE)</a>"""
            if 'plot' in self.pythia:
                out += ' <a href="./Events/%(run_name)s_plots_pythia.html">plots</a>'
            out += '</td></tr>'
        elif web and not running and self['nb_event']:
            out += """<tr><td> Pythia Events : </td><td><center>
                       <FORM ACTION="http://%(web)s/cgi-bin/RunProcess/handle_runs-pl"  ENCTYPE="multipart/form-data" METHOD="POST">
                       <INPUT TYPE=HIDDEN NAME=directory VALUE="%(me_dir)s"> 
                       <INPUT TYPE=HIDDEN NAME=whattodo VALUE="pythia"> 
                       <INPUT TYPE=HIDDEN NAME=run VALUE="%(run_name)s"> 
                       <INPUT TYPE=SUBMIT VALUE="Run Pythia"></FORM><center></td>
                       </table>"""
            return out 

        if self.pgs:
            out += '<tr><td>Reco. Objects. (PGS) : </td><td>'
            if 'log' in self.pgs:
                out += """ <a href="./Events/%(run_name)s_pgs.log">LOG</a>"""
            if 'lhco' in self.pgs:
                link = './Events/%(run_name)s_pgs_events.lhco'
                level = 'pgs'
                name = 'LHCO'                
                out += self.special_link(link, level, name)  
            if 'root' in self.pgs:
                out += """ <a href="./Events/%(run_name)s_pgs_events.root">rootfile</a>"""    
            if 'plot' in self.pgs:
                out += """ <a href="./Events/%(run_name)s_plots_pgs.html">plots</a>"""
            out += '</td></tr>'
        if self.delphes:
            out += '<tr><td>Reco. Objects. (Delphes) : </td><td>'
            if 'log' in self.delphes:
                out += """ <a href="./Events/%(run_name)s_delphes.log">LOG</a>"""
            if 'lhco' in self.delphes:
                link = './Events/%(run_name)s_delphes_events.lhco'
                level = 'pgs'
                name = 'LHCO'                
                out += self.special_link(link, level, name)
            if 'root' in self.delphes:
                out += """ <a href="./Events/%(run_name)s_delphes_events.root">rootfile</a>"""    
            if 'plot' in self.delphes:
                out += """ <a href="./Events/%(run_name)s_plots_delphes.html">plots</a>"""            
            out += '</td></tr>'
        
        if not (self.pgs or self.delphes) and web and not running and self['nb_event']:
            out += """<tr><td> Reco. Objects: </td><td><center>
                       <FORM ACTION="http://%(web)s/cgi-bin/RunProcess/handle_runs-pl"  ENCTYPE="multipart/form-data" METHOD="POST">
                       <INPUT TYPE=HIDDEN NAME=directory VALUE="%(me_dir)s"> 
                       <INPUT TYPE=HIDDEN NAME=whattodo VALUE="pgs"> 
                       <INPUT TYPE=HIDDEN NAME=run VALUE="%(run_name)s"> 
                       <INPUT TYPE=SUBMIT VALUE="Run Det. Sim."></FORM></center></td>
                       </table>"""
            return out             
        
        out += '</table>'
        return out
        
    
    
    
    
    




