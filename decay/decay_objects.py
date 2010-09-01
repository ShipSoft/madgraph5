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
"""Definition for the objects used in the decay module."""

import array
import cmath
import copy
import itertools
import logging
import math
import os
import re

import madgraph.core.base_objects as base_objects
import madgraph.core.diagram_generation as diagram_generation
import madgraph.core.color_amp as color_amp
import madgraph.core.color_algebra as color
import madgraph.iolibs.import_ufo as import_ufo
from madgraph import MadGraph5Error, MG5DIR

ZERO = 0
#===============================================================================
# Logger for decay_module
#===============================================================================

logger = logging.getLogger('decay')

#===============================================================================
# DecayParticle
#===============================================================================
class DecayParticle(base_objects.Particle):
    """DecayParticle is the the particle used in the decay module.
       It will list all the corresponding vertices
       (2_body_decay_vertices and 3_body_decay_vertices) with
       the on-shell conditions specified.
    """
    sorted_keys = ['name', 'antiname', 'spin', 'color',
                   'charge', 'mass', 'width', 'pdg_code',
                   'texname', 'antitexname', 'line', 'propagating',
                   'is_part', 'self_antipart', 
                   'decay_vertexlist'
                  ]


    def __init__(self, init_dict={}):
        """Creates a new particle object. If a dictionary is given, tries to 
        use it to give values to properties.
        A repeated assignment is to avoid error of inconsistent pdg_code and
        initial particle id of vertex"""

        dict.__init__(self)
        self.default_setup()

        assert isinstance(init_dict, dict), \
                            "Argument %s is not a dictionary" % repr(init_dict)

        #To avoid the pdg_code remain 0 and then induce the error when
        #set the vertexlist
        try:
            pid = init_dict['pdg_code']
            self.set('pdg_code', pid)
        except KeyError:
            pass
            
        for item in init_dict.keys():
            self.set(item, init_dict[item])

        #log of the decay_vertexlist_written history
        self.decay_vertexlist_written = False

    def default_setup(self):
        """Default values for all properties"""
        
        super(DecayParticle, self).default_setup()

        # The decay_vertexlist contain a list of real decay vertex
        # and one for pseudo decay vertex.
        # n_body_decay_vertexlist[0](or [False]): off-shell decay;
        # n_body_decay_vertexlist[1](or [True] ):on-shell decay.

        self['decay_vertexlist'] = {(2, False) : base_objects.VertexList(),
                                    (2, True)  : base_objects.VertexList(),
                                    (3, False) : base_objects.VertexList(),
                                    (3, True)  : base_objects.VertexList()}


    
    def check_decay_condition(self, partnum, onshell, 
                              value = base_objects.VertexList(), model = {}):
        """Check the validity of decay condition, including,
           partnum: final state particle number,
           onshell: on-shell condition,
           value  : the assign vertexlist
           model  : the specific model"""

        #Check if partnum is an integer.
        if not isinstance(partnum, int):
            raise self.PhysicsObjectError, \
                "Final particle number %s must be an integer." % str(partnum)

        #Check if partnum is 2 or 3.
        #If so, return the vertexlist with the on-shell condition.
        if partnum not in [2 ,3]:
            raise self.PhysicsObjectError, \
                "Final particle number %s must be 2 or 3." % str(partnum)
        
        #Check if onshell condition is Boolean number.
        if not isinstance(onshell, bool):
            raise self.PhysicsObjectError, \
                "%s must be a Boolean number" % str(onshell)
                
        #Check if the value is a Vertexlist(in base_objects) or a list of vertex
        if not isinstance(value, base_objects.VertexList):
            raise self.PhysicsObjectError, \
                "%s must be VertexList type." % str(value)
                    
        #Check if the model is a valid object.
        if not (isinstance(model, base_objects.Model) or model == {}):
            raise self.PhysicsObjectError, \
                "%s must be a Model" % str(model)
        elif model:
            #Check if the mother particle is in the 'model'
            if not (self.get_pdg_code() in model.get('particle_dict').keys()):
                raise self.PhysicsObjectError, \
                    "The model, %s, does not contain particle %s." \
                    %(model.get('name'), self.get_name())
        

    def check_vertexlist(self, partnum, onshell, value, model = {}):
        """Check if the all the vertex in the vertexlist satisfy the following
           conditions. If so, return true; if not, raise error messages.

           1. There is an appropriate leg for initial particle.
           2. The number of final particles equals to partnum.
           3. If model is not None, check the onshell condition and
              the initial particle id is the same as calling particle.
        """
        #Check the validity of arguments first
        self.check_decay_condition(partnum, onshell, value, model)
       
        #Determine the number of final particles.
        #Find all the possible initial particle(s).
        #Check onshell condition if the model is given.
        if not model:
            #No need to check the on-shell condition and initial particle id
            for vert in value:
                #Reset the number of initial/final particles,
                #initial particle id, and total and initial mass
                num_ini = 0
                num_radiation = 0
                num_final = 0
                
                for leg in vert.get('legs'):
                    #Identify the initial particle
                    if leg.get('id') == self.get_pdg_code():
                        #Leg id == self id, the leg is incoming if state==False.
                        if not leg.get('state'):
                            num_ini = 1
                        #state = True is fine for self_antipart
                        elif self['self_antipart']:
                            num_ini = 1
                            if num_ini ==1:
                                num_radiation = 1                
                        #state == True, id == pdg_code, not self_antipart:
                        #candidate for radiation final state
                        else:
                            num_radiation = 1
                    elif leg.get('id') == -self.get_pdg_code():
                        if leg.get('state'):
                            num_ini = 1
                        #Incoming anti_particle, candidate for radiation final
                        #state
                        else:
                            num_radiation = 1
                #Calculate the final particle number
                num_final = len(vert.get('legs'))-num_ini
                
                #Check the number of final particles is the same as partnum
                if num_final != partnum:
                    raise self.PhysicsObjectError, \
                        "The vertex is a %s -body decay, not a %s -body one."\
                        % (str(num_final), str(partnum))

                #Check if there is any appropriate leg as initial particle
                if num_ini == 0:
                    raise self.PhysicsObjectError, \
                        "There is no leg satisfied the mother particle %s"\
                        % str(self.get_pdg_code())
                #Check if the vertex is radiation
                if num_radiation != 0:
                    raise self.PhysicsObjectError, \
                        "The vertex %s is radiactive for mother particle %s"\
                        % (str(vert), str(self.get_pdg_code()))
                
        #Model is not None, check the on-shell condition
        else:
            if (self.get('mass') == 'ZERO') and (len(value) != 0):
                raise self.PhysicsObjectError, \
                    "Massless particle %s cannot decay." % self['name']
            for vert in value:
                #Reset the number of initial/final particles,
                #initial particle id, and total and initial mass
                num_ini = 0
                num_radiation = 0
                num_final = 0
                
                total_mass = 0
                ini_mass = 0

                for leg in vert.get('legs'):
                    #Calculate the total mass
                    total_mass += eval(model.get_particle(leg['id'])['mass'])

                    #Identify the initial particle
                    if leg.get('id') == self.get_pdg_code():
                        #Leg id == self id, the leg is incoming if state==False.
                        if not leg.get('state'):
                            num_ini = 1
                            ini_mass = eval(model.get_particle(leg['id'])['mass'])
                        #state = True is fine for self_antipart
                        elif self['self_antipart']:
                            num_ini = 1
                            if num_ini:
                                num_radiation = 1                
                        #state == True, id == pdg_code, not self_antipart:
                        #candidate for radiation final state
                        else:
                            num_radiation = 1
                    elif leg.get('id') == -self.get_pdg_code():
                        if leg.get('state'):
                            num_ini = 1
                            ini_mass = eval(model.get_particle(leg['id'])['mass'])
                        #Incoming anti_particle, candidate for radiation final
                        #state
                        else:
                            num_radiation = 1

                #Calculate the final particle number
                num_final = len(vert.get('legs'))-num_ini


                #Check the number of final particles is the same as partnum
                if num_final != partnum:
                    raise self.PhysicsObjectError, \
                        "The vertex is a %s -body decay, not a %s -body one."\
                        % (str(num_final), str(partnum))

                #Check if there is any appropriate leg as initial particle.
                if num_ini == 0:
                    raise self.PhysicsObjectError, \
                        "There is no leg satisfied the mother particle %s"\
                        % str(self.get_pdg_code())

                #Check the onshell condition
                if (ini_mass.real > (total_mass.real - ini_mass.real))!=onshell:
                    raise self.PhysicsObjectError, \
                        "The on-shell condition is not satisfied."

                #Check if the vertex is radiation
                if num_radiation != 0:
                    raise self.PhysicsObjectError, \
                        "The vertex is radiactive for mother particle %s"\
                        % str(self.get_pdg_code())

        return True


    def filter(self, name, value):
        """Filter for valid DecayParticle vertexlist."""
        
        if name == 'decay_vertexlist':

            #Value must be a list of 2 elements.
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                    "Decay_vertexlist %s is not a dictionary." % str(value)

            for key, item in value.items():
                if not isinstance(key, tuple):
                    raise self.PhysicsObjectError,\
                        "Key %s must be a tuple." % str(key)
                
                if len(key) != 2:
                    raise self.PhysicsObjectError,\
                        "Key %s must have two elements." % str(key)
                
                self.check_vertexlist(key[0], key[1], item)
            
        super(DecayParticle, self).filter(name, value)

        return True

    def get_vertexlist(self, partnum ,onshell):
        """Return the n-body decay vertexlist.
           partnum = n.
           If onshell=false, return the on-shell list and vice versa.
        """
        #check the validity of arguments
        self.check_decay_condition(partnum, onshell)
        
        return self.get('decay_vertexlist')[(partnum, onshell)]


    def set_vertexlist(self, partnum ,onshell, value, model = {}):
        """Set the n_body_decay_vertexlist,
           partnum: n, 
           onshell: True for on-shell decay, and False for off-shell
           value: the decay_vertexlist that is tried to assign.
           model: the underlying model for vertexlist
                  Use to check the correctness of on-shell condition.
        """
        #Check the vertexlist by check_vertexlist
        #Error is raised (by check_vertexlist) if value is not valid
        if self.check_vertexlist(partnum, onshell, value, model):
            self['decay_vertexlist'][(partnum, onshell)] = value
              
    def find_vertexlist(self, model, option=False):
        """Find the possible decay channel to decay,
           for both on-shell and off-shell.
           If option=False (default), 
           do not rewrite the VertexList if it exists.
           If option=True, rewrite the VertexList anyway.
        """
        
        #Raise error if self is not in model.
        if not (self.get_pdg_code() in model.get('particle_dict').keys()):
            raise self.PhysicsObjectError, \
                    "The parent particle %s is not in the model %s." \
                        % (self.get('name'), model.get('name'))

        #Raise error if option is not Boolean value
        if not isinstance(option, bool):
            raise self.PhysicsObjectError, \
                    "The option %s must be True or False." % str(option)
        
        #If 'decay_vertexlist_written' is true and option is false,
        #no action is proceed.
        if self.decay_vertexlist_written and not option:
            return 'The vertexlist has been setup.', \
                'No action proceeds because of False option.'

        #Reset the decay vertex before finding
        self['decay_vertexlist'] = {(2, False) : base_objects.VertexList(),
                                    (2, True)  : base_objects.VertexList(),
                                    (3, False) : base_objects.VertexList(),
                                    (3, True)  : base_objects.VertexList()}
        
        if self.get('mass') == 'ZERO':
            return

        #Go through each interaction...
        for temp_int in model.get('interactions'):
            #Save the particle dictionary (pdg_code & anti_pdg_code to particle)
            partlist = temp_int.get('particles')

            #The final particle number = total particle -1
            partnum = len(partlist)-1
            #Allow only 2 and 3 body decay
            if partnum > 3:
                continue

            #Check if the interaction contains mother particle
            if model.get_particle(self.get_anti_pdg_code()) in partlist:
                #Exclude radiation
                if self in partlist:
                    continue

                final_mass = 0
                ini_mass = eval(self.get('mass'))
                vert = base_objects.Vertex()
                legs = base_objects.LegList()
                legs.append(base_objects.Leg({
                            'id':self.get_pdg_code(),
                            'number': 0,
                            'state': False,
                            'from_group': True})
                            )

                #ini_index: record the index of initial particle if found
                ini_found = False

                #Setup all the legs and find final_mass
                for part in partlist:
                    #Not initial particle or initial particle has been setup.
                    if (part != model.get_particle(self.get_anti_pdg_code())) or ini_found:
                        legs.append(base_objects.Leg({
                                    'id': part.get_pdg_code(),
                                    'number': 0,
                                    'state': True,
                                    'from_group': True})
                                    )
                        final_mass += eval(part.get('mass'))
                    #Initial particle has not been found: ini_found = True
                    if (part == model.get_particle(self.get_anti_pdg_code())) and (not ini_found):
                        
                        ini_found = True
                    
                #Sort the leglist for comparison sake (removable!)
                legs.sort(legcmp)

                vert.set('id', temp_int.get('id'))
                vert.set('legs', legs)
                temp_vertlist = base_objects.VertexList([vert])
                #Force the mass to be real for safety.
                ini_mass, final_mass = ini_mass.real, final_mass.real

                #Check validity of vertex (removable)
                """self.check_vertexlist(partnum,
                ini_mass > final_mass,
                temp_vertlist, model)"""

                #Append current vert to vertexlist
                self['decay_vertexlist'][(partnum, ini_mass > final_mass)].\
                    append(vert)

        #Set the decay_vertexlist_written at the end
        self.decay_vertexlist_written = True



#Helping function
def legcmp(x, y):
    """Define the leg comparison, useful when testEqual is execute"""
    mycmp = cmp(x['id'], y['id'])
    if mycmp == 0:
        mycmp = cmp(x['state'], y['state'])
    return mycmp

#===============================================================================
# DecayParticleList
#===============================================================================
class DecayParticleList(base_objects.ParticleList):
    """A class to store list of DecayParticle, Particle is also a valid
       element, but will automatically convert to DecayParticle"""

    def append(self, object):
        """Append DecayParticle, even if object is Particle"""

        assert self.is_valid_element(object), \
            "Object %s is not a valid object for the current list" %repr(object)

        if isinstance(object, DecayParticle):
            list.append(self, object)
        else:
            list.append(self, DecayParticle(object))

    def generate_dict(self):
        """Generate a dictionary from particle id to particle.
        Include antiparticles.
        """

        particle_dict = {}

        for particle in self:
            particle_dict[particle.get('pdg_code')] = particle
            if not particle.get('self_antipart'):
                antipart = copy.deepcopy(particle)
                antipart.set('is_part', False)
                particle_dict[antipart.get_pdg_code()] = antipart

        return particle_dict
    
#===============================================================================
# DecayModel: Model object that is used in this module
#===============================================================================
class DecayModel(base_objects.Model):
    """Model object with an attribute to construct the decay vertex list
       for a given particle and a interaction
    """

    def __init__(self, ini_dict = {}):
        """Reset the particle_dict so that items in it is 
           of DecayParitcle type"""
        super(DecayModel, self).__init__(ini_dict)

        self['particle_dict'] = {}
        self.get('particle_dict')
        
    def default_setup(self):
        """The particles is changed to ParticleList"""
        super(DecayModel, self).default_setup()
        self['particles'] = DecayParticleList()

    def set(self, name, value):
        """Change the Particle into DecayParticle"""
        #Record the validity of set by mother routine
        return_value = super(DecayModel, self).set(name, value)
        #Reset the dictionaries

        if return_value:
            if name == 'particles':
                #Reset dictionaries
                self['particle_dict'] = {}
                self['got_majoranas'] = None
                #Convert to DecayParticleList
                self['particles'] = DecayParticleList(value)
                #Generate new dictionaries with items are DecayParticle
                self.get('particle_dict')
                self.get('got_majoranas')
            if name == 'interactions':
                # Reset dictionaries
                self['interaction_dict'] = {}
                self['ref_dict_to1'] = {}
                self['ref_dict_to0'] = {}
                #Generate interactions with particles are DecayParticleLis
                for inter in self['interactions']:
                    inter['particles']=DecayParticleList([part for part in \
                                                          inter['particles']])
                # Generate new dictionaries
                self.get('interaction_dict')
                self.get('ref_dict_to1')
                self.get('ref_dict_to0')

        return return_value

    def find_vertexlist(self):
        """ Check whether the interaction is able to decay from mother_part.
            Set the '2_body_decay_vertexlist' and 
            '3_body_decay_vertexlist' of the corresponding particles.
            Utilize in finding all the decay table of the whole model
        """
    
        ini_list = []
        #Dict to store all the vertexlist (for convenient removable!)
        vertexlist_dict = {}
        for part in self.get('particles'):
            if part['mass'] != 'ZERO':
                #All valid initial particles (mass != 0 and is_part == True)
                ini_list.append(part.get_pdg_code())
            for partnum in [2, 3]:
                for onshell in [False, True]:
                    vertexlist_dict[(part.get_pdg_code(), partnum, onshell)] = \
                        base_objects.VertexList()

        #Prepare the vertexlist
        for inter in self['interactions']:
            #Calculate the particle number and exclude partnum > 3
            partnum = len(inter['particles']) - 1
            if partnum > 3:
                continue
            
            temp_legs = base_objects.LegList()
            total_mass = 0
            validity = False
            for num, part in enumerate(inter['particles']):
                #Check if the interaction contains valid initial particle
                if part.get_anti_pdg_code() in ini_list:
                    validity = True

                #Create the original legs
                temp_legs.append(base_objects.Leg({'id':part.get_pdg_code()}))
                total_mass += eval(part.get('mass')).real
            
            #Exclude interaction without valid initial particle
            if not validity:
                continue

            for num, part in enumerate(inter['particles']):
                #Get anti_pdg_code (pid for incoming particle)
                pid = part.get_anti_pdg_code()
                #Exclude invalid initial particle
                if pid not in ini_list:
                    continue

                #Exclude initial particle appears in final particles
                #i.e. radiation is excluded.
                if self.get_particle(pid) in (inter['particles'][:num] + \
                                                  inter['particles'][num+1:]):
                    continue

                #Create new legs for the sort later
                temp_legs_new = copy.deepcopy(temp_legs)

                #Set each leg as incoming particle
                temp_legs_new[num].set('state', False)
                temp_legs_new[num].set('id', pid)

                ini_mass = eval(part.get('mass')).real
                onshell = ini_mass > (total_mass - ini_mass)

                
                #Sort the legs for comparison
                temp_legs_new.sort(legcmp)
                temp_vertex = base_objects.Vertex({'id': inter.get('id'),
                                                   'legs':temp_legs_new})

                #Record the vertex with key = (interaction_id, part_id)
                if temp_vertex not in vertexlist_dict[(pid, partnum, onshell )]:
                    vertexlist_dict[(pid, partnum, onshell)].append(temp_vertex)
                    #Assign temp_vertex to antiparticle of part
                    #particle_dict[pid].check_vertexlist(partnum, onshell, 
                    #             base_objects.VertexList([temp_vertex]), self)
                    self.get_particle(pid)['decay_vertexlist'][(partnum, onshell)].append(temp_vertex)


        fdata = open(os.path.join(MG5DIR, 'models', self['name'], 'vertexlist_dict.dat'), 'w')
        fdata.write(str(vertexlist_dict))
        fdata.close()



    def read_param_card(self, param_card):
        """Read a param_card and set all parameters and couplings as
        members of this module"""

        if not os.path.isfile(param_card):
            raise MadGraph5Error, \
                  "No such file %s" % param_card

        # Extract external parameters
        external_parameters = self['parameters'][('external',)]

        # Create a dictionary from LHA block name and code to parameter name
        parameter_dict = {}
        for param in external_parameters:
            try:
                dict = parameter_dict[param.lhablock.lower()]
            except KeyError:
                dict = {}
                parameter_dict[param.lhablock.lower()] = dict
            dict[tuple(param.lhacode)] = param.name
            
        # Now read parameters from the param_card

        # Read in param_card
        param_lines = open(param_card, 'r').read().split('\n')

        # Define regular expressions
        re_block = re.compile("^block\s+(?P<name>\w+)")
        re_decay = re.compile("^decay\s+(?P<pid>\d+)\s+(?P<value>[\d\.e\+-]+)")
        re_single_index = re.compile("^\s*(?P<i1>\d+)\s+(?P<value>[\d\.e\+-]+)")
        re_double_index = re.compile(\
                       "^\s*(?P<i1>\d+)\s+(?P<i2>\d+)\s+(?P<value>[\d\.e\+-]+)")
        block = ""
        # Go through lines in param_card
        for line in param_lines:
            if not line.strip() or line[0] == '#':
                continue
            line = line.lower()
            # Look for blocks
            block_match = re_block.match(line)
            if block_match:
                block = block_match.group('name')
                continue
            # Look for single indices
            single_index_match = re_single_index.match(line)
            if block and single_index_match:
                i1 = int(single_index_match.group('i1'))
                value = single_index_match.group('value')
                try:
                    exec("globals()[\'%s\'] = %s" % (parameter_dict[block][(i1,)],
                                      value))
                    logger.info("Set parameter %s = %f" % \
                                (parameter_dict[block][(i1,)],\
                                 eval(parameter_dict[block][(i1,)])))
                except KeyError:
                    logger.warning('No parameter found for block %s index %d' %\
                                   (block, i1))
                continue
            double_index_match = re_double_index.match(line)
            # Look for double indices
            if block and double_index_match:
                i1 = int(double_index_match.group('i1'))
                i2 = int(double_index_match.group('i2'))
                try:
                    exec("globals()[\'%s\'] = %s" % (parameter_dict[block][(i1,i2)],
                                      double_index_match.group('value')))
                    logger.info("Set parameter %s = %f" % \
                                (parameter_dict[block][(i1,i2)],\
                                 eval(parameter_dict[block][(i1,i2)])))
                except KeyError:
                    logger.warning('No parameter found for block %s index %d %d' %\
                                   (block, i1, i2))
                continue
            # Look for decays
            decay_match = re_decay.match(line)
            if decay_match:
                block = ""
                pid = int(decay_match.group('pid'))
                value = decay_match.group('value')
                try:
                    exec("globals()[\'%s\'] = %s" % \
                         (parameter_dict['decay'][(pid,)],
                          value))
                    logger.info("Set decay width %s = %f" % \
                                (parameter_dict['decay'][(pid,)],\
                                 eval(parameter_dict['decay'][(pid,)])))
                except KeyError:
                    logger.warning('No decay parameter found for %d' % pid)
                continue

        # Define all functions used
        for func in self['functions']:
            exec("def %s(%s):\n   return %s" % (func.name,
                                                ",".join(func.arguments),
                                                func.expr))

        # Extract derived parameters
        # TO BE IMPLEMENTED allow running alpha_s coupling
        derived_parameters = []
        try:
            derived_parameters += self['parameters'][()]
        except KeyError:
            pass
        try:
            derived_parameters += self['parameters'][('aEWM1',)]
        except KeyError:
            pass
        try:
            derived_parameters += self['parameters'][('aS',)]
        except KeyError:
            pass
        try:
            derived_parameters += self['parameters'][('aS', 'aEWM1')]
        except KeyError:
            pass
        try:
            derived_parameters += self['parameters'][('aEWM1', 'aS')]
        except KeyError:
            pass

        # Now calculate derived parameters
        # TO BE IMPLEMENTED use running alpha_s for aS-dependent params
        for param in derived_parameters:
            exec("globals()[\'%s\'] = %s" % (param.name, param.expr))
            if not eval(param.name) and eval(param.name) != 0:
                logger.warning("%s has no expression: %s" % (param.name,
                                                             param.expr))
            try:
                logger.info("Calculated parameter %s = %f" % \
                            (param.name, eval(param.name)))
            except TypeError:
                logger.info("Calculated parameter %s = (%f, %f)" % \
                            (param.name,\
                             eval(param.name).real, eval(param.name).imag))
        
        # Extract couplings
        couplings = []
        try:
            couplings += self['couplings'][()]
        except KeyError:
            pass
        try:
            couplings += self['couplings'][('aEWM1',)]
        except KeyError:
            pass
        try:
            couplings += self['couplings'][('aS',)]
        except KeyError:
            pass
        try:
            couplings += self['couplings'][('aS', 'aEWM1')]
        except KeyError:
            pass
        try:
            couplings += self['couplings'][('aEWM1', 'aS')]
        except KeyError:
            pass

        # Now calculate all couplings
        # TO BE IMPLEMENTED use running alpha_s for aS-dependent couplings
        for coup in couplings:
            exec("globals()[\'%s\'] = %s" % (coup.name, coup.expr))
            if not eval(coup.name) and eval(coup.name) != 0:
                logger.warning("%s has no expression: %s" % (coup.name,
                                                             coup.expr))
            logger.info("Calculated coupling %s = (%f, %f)" % \
                        (coup.name,\
                         eval(coup.name).real, eval(coup.name).imag))
                


    def find_decay_groups(self):
        """Find groups of particles which can decay into each other,
        keeping Standard Model particles outside for now. This allows
        to find particles which are absolutely stable based on their
        interactions.

        Algorithm:

        1. Start with any non-SM particle. Look for all
        interactions which has this particle in them.

        2. Any particles with single-particle interactions with this
        particle and with any number of SM particles are in the same
        decay group.

        3. If any of these particles have decay to only SM
        particles, the complete decay group becomes "sm"
        
        5. Iterate through all particles, to cover all particles and
        interactions.
        """

        self.sm_ids = [1,2,3,4,5,6,11,12,13,14,15,16,21,22,23,24]
        self.decay_groups = [[]]

        particles = [p for p in self.get('particles') if \
                     p.get('pdg_code') not in self.sm_ids]

        for particle in particles:
            # Check if particles is already in a decay group
            if particle not in sum(self.decay_groups, []):
                # Insert particle in new decay group
                self.decay_groups.append([particle])
                self.find_decay_groups_for_particle(particle)

    def find_decay_groups_for_particle(self, particle):
        """Recursive routine to find decay groups starting from a
        given particle.

        Algorithm:

        1. Pick out all interactions with this particle

        2. For any interaction which is not a radiation (i.e., has
        this particle twice): 

        a. If there is a single non-sm particle in
        the decay, add particle to this decay group. Otherwise, add to
        SM decay group or new decay group.

        b. If there are more than 1 non-sm particles: if all particles
        in decay groups, merge decay groups according to different
        cases:
        2 non-sm particles: either both are in this group, which means
        this is SM, or one is in this group, so the other has to be
        SM, or both are in the same decay group, then this group is SM.
        3 non-sm particles: either 1 is in this group, then the other
        two must be in same group or 2 is in this group, then third
        must also be in this group, or 2 is in the same group, then
        third must be in this group (not yet implemented). No other
        cases can be dealt with.
        4 or more: Not implemented (not phenomenologically interesting)."""
        
        # interactions with this particle which are not radiation
        interactions = [i for i in self.get('interactions') if \
                            particle in i.get('particles') and \
                            i.get('particles').count(particle) == 1 and \
                            (particle.get('self_antipart') or
                             not self.get_particle(particle.get_anti_pdg_code()) \
                                 in i.get('particles'))]
                             
        while interactions:
            interaction = interactions.pop(0)
            non_sm_particles = [p for p in interaction.get('particles') \
                                if p != particle and \
                                not p.get('pdg_code') in self.sm_ids and \
                                not (p.get('is_part') and p in \
                                     self.decay_groups[0] or \
                                     not p.get('is_part') and \
                                     self.get_particle(p.get('pdg_code')) in \
                                     self.decay_groups[0])]
            group_index = [i for (i, g) in enumerate(self.decay_groups) \
                           if particle in g][0]

            if len(non_sm_particles) == 0:
                # The decay group of this particle is the SM group
                if group_index > 0:
                    group = self.decay_groups.pop(group_index)
                    self.decay_groups[0].extend(group)
                    
            elif len(non_sm_particles) == 1:
                # The other particle should be in my decay group
                particle2 = non_sm_particles[0]
                if not particle2.get('is_part'):
                    particle2 = self.get_particle(particle2.get_anti_pdg_code())
                if particle2 in self.decay_groups[group_index]:
                    # This particle is already in this decay group,
                    # and has been treated.
                    continue
                elif particle2 in sum(self.decay_groups, []):
                    # This particle is in a different decay group - merge
                    group_index2 = [i for (i, g) in \
                                    enumerate(self.decay_groups) \
                                    if particle2 in g][0]
                    group = self.decay_groups.pop(max(group_index,
                                                      group_index2))
                    self.decay_groups[min(group_index, group_index2)].\
                                                        extend(group)
                else:
                    # Add particle2 to this decay group
                    self.decay_groups[group_index].append(particle2)

            elif len(non_sm_particles) > 1:
                # Check if any of the particles are not already in any
                # decay group. If there are any, let another particle
                # take care of this interaction instead, later on.

                non_checked_particles = [p for p in non_sm_particles if \
                                         (p.get('is_part') and not p in \
                                          sum(self.decay_groups, []) or \
                                          not p.get('is_part') and not \
                                          self.get_particle(\
                                                     p.get_anti_pdg_code()) in \
                                          sum(self.decay_groups, []))
                                         ]

                if not non_checked_particles:
                    # All particles have been checked. Analyze interaction.

                    if len(non_sm_particles) == 2:
                        # Are any of the particles in my decay group already?
                        this_group_particles = [p for p in non_sm_particles \
                                                if p in self.decay_groups[\
                                                                   group_index]]
                        if len(this_group_particles) == 2:
                            # There can't be any conserved quantum
                            # number! Should be SM group!
                            group = self.decay_groups.pop(group_index)
                            self.decay_groups[0].extend(group)
                            continue
                        elif len(this_group_particles) == 1:
                            # One particle is in the same group as this particle
                            # The other (still non_sm yet) must be SM group.
                            particle2 = [p for p in non_sm_particles \
                                             if p != this_group_particles[0]][0]
                            if not particle2.get('is_part'):
                                particle2 = self.get_particle(particle2.get_anti_pdg_code())

                            group_index2 = [i for (i, g) in \
                                                enumerate(self.decay_groups)\
                                                if particle2 in g][0]
                            group_2 = self.decay_groups.pop(group_index2)
                            self.decay_groups[0].extend(group_2)

                        else:
                            # If the two particles are in another same group,
                            # this particle must be the SM particle.
                            # Transform the 1st non_sm_particle into particle
                            particle1 = non_sm_particles[0]
                            if not particle1.get('is_part'):
                                particle1 = self.get_particle(\
                                    particle1.get_anti_pdg_code())
                            # Find the group of particle1
                            group_index1 = [i for (i, g) in \
                                            enumerate(self.decay_groups) \
                                            if particle1 in g][0]

                            # If the other non_sm_particle is in the same group
                            # as particle1, try to merge this particle to SM
                            if non_sm_particles[1] in \
                                    self.decay_groups[group_index1]:
                                if group_index > 0:
                                    group = self.decay_groups.pop(group_index)
                                    self.decay_groups[0].extend(group)

                    if len(non_sm_particles) == 3:
                        # Are any of the particles in my decay group already?
                        this_group_particles = [p for p in non_sm_particles \
                                                if p in self.decay_groups[\
                                                                   group_index]]
                        if len(this_group_particles) == 2:
                            # Also the 3rd particle has to be in this group.
                            # Merge.
                            particle2 = [p for p in non_sm_particles if p not \
                                         in this_group_particles][0]
                            if not particle2.get('is_part'):
                                particle2 = self.get_particle(\
                                                  particle2.get_anti_pdg_code())
                            group_index2 = [i for (i, g) in \
                                            enumerate(self.decay_groups) \
                                            if particle2 in g][0]
                            group = self.decay_groups.pop(max(group_index,
                                                              group_index2))
                            self.decay_groups[min(group_index, group_index2)].\
                                                                extend(group)
                        if len(this_group_particles) == 1:
                            # The other two particles have to be in
                            # the same group
                            other_group_particles = [p for p in \
                                                     non_sm_particles if p not \
                                                     in this_group_particles]
                            particle1 = other_group_particles[0]
                            if not particle1.get('is_part'):
                                particle1 = self.get_particle(\
                                                  particle1.get_anti_pdg_code())
                            group_index1 = [i for (i, g) in \
                                            enumerate(self.decay_groups) \
                                            if particle1 in g][0]
                            particle2 = other_group_particles[0]
                            if not particle2.get('is_part'):
                                particle2 = self.get_particle(\
                                                  particle2.get_anti_pdg_code())
                            group_index2 = [i for (i, g) in \
                                            enumerate(self.decay_groups) \
                                            if particle2 in g][0]

                            if group_index1 != group_index2:
                                # Merge groups
                                group = self.decay_groups.pop(max(group_index1,
                                                                  group_index2))
                                self.decay_groups[min(group_index1,
                                                      group_index2)].\
                                                                   extend(group)

                        # One more case possible to say something
                        # about: When two of the three particles are
                        # in the same group, the third particle has to
                        # be in the present particle's group. I'm not
                        # doing this case now though.

                    # For cases with number of non-sm particles > 3,
                    # There are also possibilities to say something in
                    # particular situations. Don't implement this now
                    # however.

#===============================================================================
# Channel: Each channel for the decay
#===============================================================================
class Channel(base_objects.Diagram):
    """Channel: a diagram that describes a certain on-shell decay channel
                with apprximated (mean) matrix element, phase space area,
                and decay width
                ('apx_matrixelement', 'apx_PSarea', and  'apx_decaywidth')
                Model must be specified.
    """

    sorted_keys = ['vertices',
                   'model',
                   'apx_matrixelement', 'apx_PSarea', 'apx_decaywidth']

    def def_setup(self):
        """Default values for all properties"""
        
        self['vertices'] = VertexList()
        self['model'] = Model()
        self['apx_matrixelement', 'apx_PSarea', 'apx_decaywidth'] = [0., 0., 0.]

    def filter(self, name, value):
        """Filter for valid diagram property values."""
        
        if name in ['apx_matrixelement', 'apx_PSarea', 'apx_decaywidth']:
            if not isinstance(value, float):
                raise self.PhysicsObjectError, \
                    "Value %s is not a float" % str(value)
        
        if name == 'model':
            if not isinstance(value, Model):
                raise self.PhysicsObjectError, \
                        "%s is not a valid Model object" % str(value)

        super(Channel, self0).filter(self, name, value)

    def get_sorted_keys(self):
        """Return particle property names as a nicely sorted list."""

        return self.sorted_keys

    def nice_string(self):
        pass

    def get_initial_id(self):
        """ Return the list of the id of initial particle"""
        pass

    def get_final_ids(self):
        """ Return the list of the ids of final particles"""
        pass
        
    def get_apx_matrixelement(self):
        """calculate the apx_matrixelement"""
        pass

    def get_apx_PSarea(self):
        """calculate the apx_PSarea"""

        # The initial particle mass
        M = self['model'].get_particle(self.get_initial_id()[0])['mass']

        if len(self.get_final_ids()) == 2:
            
            m_1 = self['model'].get_particle(self.get_final_ids()[0])['mass']
            m_2 = self['model'].get_particle(self.get_final_ids()[1])['mass']

            apx_PSarea = 1 / (32 * math.pi ) * \
                         math.sqrt((M-m_1^2-m_2^2)^2-4*m_1^2*m_2^2)

        elif self.get_num_finalparticles() == 3:
            # Calculate the phase space area for 3 body decay
            m_1 = self['model'].get_particle(self.get_final_ids()[0])['mass']
            m_2 = self['model'].get_particle(self.get_final_ids()[1])['mass']
            m_3 = self['model'].get_particle(self.get_final_ids()[2])['mass']
            
            # The middle point value of the m_1, m_2 C.M. mass
            m_12_mid = (M-m_3+m_1+m_2)/2

            E_2_dag = (m_12^2-m_1^2+m_2^2)/(2*m_12)
            E_3_dag = (M-m_12^2-m_3^2)/(2*m_12)

            apx_PSarea = 4*math.sqrt((E_2_dag^2-m_2^2)*(E_3_dag^2-m_3^2)) \
                         * ((1-m_3)^2-(m_1+m_2)^2)

        else:
            # This version cannot deal with channels with more than 3 final
            # particles.

            raise self.PhysicsObjectError, \
                    "Number of final particles larger than three.\n" \
                        "Not allow in this version."


    def get_apx_decaywidth(self):
        """Calculate the apx_decaywidth"""
        
        self.apx_decaywidth = self.get_apx_matrixelment() * self.get_apx_PSarea()

#===============================================================================
# ChannelList: List of all possible  channels for the decay
#===============================================================================
class ChannelList(base_objects.DiagramList):
    """List of decay Channel
    """

    def is_valid_element(self, obj):
        """ Test if the object is a valid Channel for the list. """

        return isinstance(obj, Channel)

    def nice_string(self, indent=0):
        """Return a nicely formatted string"""

        pass
