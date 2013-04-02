import logging.config
import logging
import pydoc
import os
import loop_me_comparator
import me_comparator
import unittest


from madgraph import MG5DIR
from madgraph import MadGraph5Error
from madgraph.iolibs.files import cp
from test_ML5 import procToFolderName

#Look for MG5/MG4 path
_mg5_path = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-3])
_file_path = os.path.dirname(os.path.realpath(__file__))
_pickle_path = os.path.join(_file_path, 'input_files', 'ML_parallel_saved_runs')

# The processes below are treated all together because they are relatively quick

HCR_processes_short = []

ML5EW_processes_short = []

# The longer processes below are treated one by one so that they can be better
# independently checked/updated (especially the corresponding reference pickle.)

HCR_processes_long =  [
                       # The process below is for testing the parallel tests only
                       ('g g > t t~ g',{'QCD':3,'QED':0},['QED'],{'QCD':6,'QED':2}),
                       ('g g > t t~ h',{'QCD':2,'QED':1},['QCD'],{'QCD':6,'QED':2}), 
                       ('g g > t t~ h',{'QCD':2,'QED':1},['QED'],{'QCD':4,'QED':4})]

HCR_processes_long_dic = dict((procToFolderName(elem[0])+'_'+'_'.join(elem[2][0].split()),elem)\
                               for elem in HCR_processes_long)

ML5EW_processes_long =  [
                         ('g g > t t~ g',{'QCD':3,'QED':0},['QED'],{'QCD':6,'QED':2}),
                       ('g g > t t~ h',{'QCD':2,'QED':1},['QCD'],{'QCD':6,'QED':2}), 
                       ('g g > t t~ h',{'QCD':2,'QED':1},['QED'],{'QCD':4,'QED':4})]

ML5EW_processes_long_dic = dict((procToFolderName(elem[0])+'_'+'_'.join(elem[2][0].split()),elem)\
                                for elem in ML5EW_processes_long)

class ML5EWTest(unittest.TestCase):
    """ A class to test ML5 EW corrections versus runs from hard-coded reference process. """

    test_model_name = 'loop_qcd_qed_sm-parallel_test'

    def setUp(self):
        """ Here we just copy the hidden restrict_card to a regular one.
        And we don't bother making it hidden again after the test."""
        cp(os.path.join(_mg5_path,'models','loop_qcd_qed_sm','.restrict_parallel_test.dat'),
           os.path.join(_mg5_path,'models','loop_qcd_qed_sm','restrict_parallel_test.dat'))

    @staticmethod
    def create_pickle(my_proc_list, pickle_file, runner, ref_runner=None,
                      model = 'loop_qcd_qed_sm-parallel_test', energy = 1000):
        """ Create a pickle with name 'pickle_file' on the specified processes
        and also possibly using the PS points provided by the reference runner """
        
        my_comp = loop_me_comparator.LoopMEComparator()
        if not ref_runner is None:
            my_comp.set_me_runners(ref_runner,runner)
        else:
            my_comp.set_me_runners(runner)
        my_comp.run_comparison(my_proc_list,model=model,energy=energy)

        loop_me_comparator.LoopPickleRunner.store_comparison( 
            os.path.join(_pickle_path,pickle_file),
            [runner.proc_list,runner.res_list],
            runner.model,runner.name,energy=runner.energy)
        
    def compare_processes(self, my_proc_list = [], model = 'loop_qcd_qed_sm-parallel_test',
            pickle_file = "", energy = 2000, tolerance = 1e-06, filename = "",
            chosen_runner = "ML5_opt"):
        """ A helper function to compare processes. 
        Note that the chosen_runner is what runner should to create the reference
        pickle if missing"""
        
        # Print out progress if it is a run for an individual process
        if len(my_proc_list)==1:
            print "\n== %s =="%my_proc_list[0][0]
        else:
            print "\n== %s =="%filename
        
        # Check if pickle exists, if not create it        
        if pickle_file!="" and not os.path.isfile(os.path.join(_pickle_path,pickle_file)):
            print " => Computing reference evaluation with %s"%chosen_runner
            self.create_loop_pickle(my_proc_list, model,
                                             pickle_file, energy, chosen_runner)
            print "\n => Done with %s evaluation"%chosen_runner
        # Load the stored runner
        if pickle_file != "":
            stored_runner = me_comparator.PickleRunner.find_comparisons(
                              os.path.join(_pickle_path,pickle_file))[0]

        # Create a MERunner object for MadLoop 5 optimized
        ML5_opt = loop_me_comparator.LoopMG5Runner()
        ML5_opt.setup(_mg5_path, optimized_output=True, temp_dir=filename)
    
        # Create a MERunner object for MadLoop 5 default
        ML5_default = loop_me_comparator.LoopMG5Runner()
        ML5_default.setup(_mg5_path, optimized_output=False, temp_dir=filename) 

        # Create and setup a comparator
        my_comp = loop_me_comparator.LoopMEComparator()
        
        # Always put the saved run first if you use it, so that the corresponding PS
        # points will be used.
        if pickle_file != "":
            my_comp.set_me_runners(stored_runner,ML5_opt,ML5_default)
        else:
            my_comp.set_me_runners(ML5_opt,ML5_default)
        
        # Run the actual comparison
        my_comp.run_comparison(my_proc_list,
                           model=model,
                           energy=energy)
        
        # Print the output
        my_comp.output_result(filename=os.path.join(_mg5_path,filename+'.log'))

        # Assert that all process comparisons passed the tolerance cut
        my_comp.assert_processes(self, tolerance)

        # Do some cleanup
        my_comp.cleanup()

    def create_loop_pickle(self, my_proc_list, model, pickle_file, energy, \
                                                                 chosen_runner):
        """ Create the pickle file for reference for the arguments here."""
#       print "Creating loop pickle for chosen_runner=",chosen_runner
        allowed_chosen_runners = ['ML5_opt','ML5_default'] 
        if chosen_runner not in allowed_chosen_runners:
            raise MadGraph5Error, 'The reference runner can only be in %s.'%\
                                                          allowed_chosen_runners
        
        runner = None
        if chosen_runner == 'ML5_opt':
            runner = loop_me_comparator.LoopMG5Runner()
            runner.setup(_mg5_path, optimized_output=True)
        if chosen_runner == 'ML5_default':
            runner = loop_me_comparator.LoopMG5Runner()
            runner.setup(_mg5_path, optimized_output=False)
        
        self.create_pickle(my_proc_list,pickle_file, runner, ref_runner=None, \
                                                      model=model,energy=energy)
        
        runner.cleanup()

    #===========================================================================
    # First tests consisting in a list of quick 2>2 processes to be run together
    #===========================================================================

    def test_short_ML5EW_sm_vs_stored_ML5EW(self):
        if ML5EW_processes_short:
            self.compare_processes(ML5EW_processes_short,model = self.test_model_name,
                                   pickle_file = 'ml5ew_short_parallel_tests.pkl',
                                        filename = 'ptest_short_ml5ew_vs_old_ml5ew',
                                                            chosen_runner='ML5')

    # The tests below probe one quite long process at a time individually, so
    # one can better manage them.
    
    #===========================================================================
    # First the long checks against results available in Hard-Coded Reference
    #===========================================================================

#   ('g g > t t~ g',{'QCD':3,'QED':0},['QED'],{'QCD':6,'QED':2})
    def test_long_sm_vs_stored_HCR_gg_ttxg_QED(self):
        proc = 'gg_ttxg_QED'
        self.compare_processes([HCR_processes_long_dic[proc]], 
               model = self.test_model_name, pickle_file = 'hcr_%s.pkl'%proc,
               filename = 'ptest_long_sm_vs_HCR_%s'%proc, chosen_runner = 'HCR')

#   ('g g > t t~ h',{'QCD':2,'QED':1},['QED'],{'QCD':4,'QED':4})    
    def test_long_sm_vs_stored_HCR_gg_ttxh_QED(self):
        proc = 'gg_ttxh_QED'
        self.compare_processes([HCR_processes_long_dic[proc]], 
               model = self.test_model_name, pickle_file = 'hcr_%s.pkl'%proc,
                                      filename = 'ptest_long_sm_vs_hcr_%s'%proc)

#   ('g g > t t~ h',{'QCD':2,'QED':1},['QCD'],{'QCD':6,'QED':2})
    def test_long_sm_vs_stored_HCR_gg_ttxh_QCD(self):
        proc = 'gg_ttxh_QCD'
        self.compare_processes([HCR_processes_long_dic[proc]], 
               model = self.test_model_name, pickle_file = 'hcr_%s.pkl'%proc,
               filename = 'ptest_long_sm_vs_hcr_%s'%proc, chosen_runner = 'HCR')


    #===========================================================================
    # Now the long checks against results previsouly generated in MadLoop 5.
    #===========================================================================

#   ('g g > h t t~',{'QCD':2,'QED':1},['QCD'],{'QCD':6,'QED':2})
# it cannot be used since the parameter of loop_qcd_qed_sm is different with loop_sm
# ml5_sm_%s.pkl is generated by loop_sm-parallel_tests 
    def test_long_sm_vs_stored_ML5EW_gg_ttxh_QCD(self):
        pass
        proc = "gg_httx"
        self.compare_processes([ML5EW_processes_long_dic[proc+'_QCD']],
               model = self.test_model_name, pickle_file = 'ml5_sm_%s.pkl'%proc,
                                  filename = 'ptest_long_sm_vs_old_ml5_%s_QCD'%proc,
                                                      chosen_runner = 'ML5_opt')


if '__main__' == __name__:
    # Get full logging info
    logging.config.fileConfig(os.path.join(_mg5_path, 'tests', '.mg5_logging.conf'))
    logging.root.setLevel(logging.INFO)
    logging.getLogger('madgraph').setLevel(logging.INFO)
    logging.getLogger('cmdprint').setLevel(logging.INFO)
    logging.getLogger('tutorial').setLevel(logging.ERROR)
        
    logging.basicConfig(level=logging.INFO)
    
    # Replace here the path of your HCR output file
    HCRpath = '/Users/erdissshaw/Works/FLibatM/check-ML/OutputML'
    model = 'loop_qcd_qed_sm--parallel_test'
    for savefile,proc in HCR_processes_long_dic:
        res_list = []
        proc_list = []
        if os.path.isfile(os.path.join(_pickle_path,"hcr_"+savefile+".pkl")):
            continue
        else:
            pickle_file = "hcr_"+savefile+".pkl"
        if not os.path.isfile(os.path.join(HCRpath,savefile+'.dat')):
            continue
        proc_list.append(proc)
        res_list.append(loop_me_comparator.LoopMG5Runner.\
        parse_check_output(file(os.path.join(HCRpath,savefile+'.dat'))))
        runner = loop_me_comparator.LoopHardCodedRefRunner()
        runner.setup(proc_list,res_list,model)
        loop_me_comparator.LoopPickleRunner.store_comparison( 
            os.path.join(_pickle_path,pickle_file),
            [runner.proc_list,runner.res_list],
            runner.model,runner.name,energy=runner.energy)
        
