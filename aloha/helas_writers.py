try:
    import madgraph.iolibs.file_writers as writers 
except:
    import aloha.writer as writers
    
import os
import re 
from numbers import Number

class WriteHelas: 
    """ Generic writing functions """ 
    
    power_symbol = '**'
    change_var_format = str
    change_number_format = str
    extension = ''
    type_to_variable = {2:'F',3:'V',5:'T',1:'S'}
    type_to_size = {'S':3, 'T':18, 'V':6, 'F':6}
    
    def __init__(self, abstracthelas, dirpath):

        self.obj = abstracthelas.expr
        helasname = get_helas_name(abstracthelas.name, abstracthelas.outgoing)
        self.out_path = os.path.join(dirpath, helasname + self.extension)
        self.dir_out = dirpath
        self.particles =  [self.type_to_variable[spin] for spin in \
                          abstracthelas.spins]
        self.namestring = helasname
        self.comment = abstracthelas.infostr
        self.offshell = abstracthelas.outgoing 
        self.symmetries = abstracthelas.symmetries

        #prepare the necessary object
        self.collect_variables() # Look for the different variables
        self.make_all_lists()   # Compute the expression for the call ordering
                                 #the definition of objects,...

    def collect_variables(self):
        """Collects Momenta,Mass,Width into lists"""
         
        MomentaList = set()
        MassList = set()
        WidthList = set()
        OverMList = set()
        for elem in self.obj.tag:
            if elem.startswith('P'):
                MomentaList.add(elem)
            elif elem.startswith('M'):
                MassList.add(elem)
            elif elem.startswith('W'):
                WidthList.add(elem)
            elif elem.startswith('O'):
                OverMList.add(elem) 

        MomentaList = list(MomentaList)
        MassList = list(MassList)
        WidthList = list(WidthList)
        OverMList = list(OverMList)
        
        self.collected = {'momenta':MomentaList, 'width':WidthList, \
                          'mass':MassList, 'om':OverMList}
        
        return self.collected

    def define_header(self): 
        """ Prototype for language specific header""" 
        pass

    def define_content(self): 
        """Prototype for language specific body""" 
        pass
    
    def define_foote (self):
        """Prototype for language specific footer"""
        pass
    
    def write_indices_part(self, indices, obj): 
        """Routine for making a string out of indice objects"""
        
        text = 'output(%s)' % indices
        return text                 
        
    def write_obj(self, obj):
        """Calls the appropriate writing routine"""

        try:
            vartype = obj.vartype
        except:
            return self.change_number_format(obj)

        if vartype == 2 : # MultVariable
            return self.write_obj_Mult(obj)
        elif not vartype: # Variable
            return self.write_obj_Var(obj)
        elif vartype == 1 : # AddVariable
            return self.write_obj_Add(obj)
        elif vartype == 5: # ConstantObject
            return self.change_number_format(obj.value)
        else: 
            raise Exception('Warning unknown object: %s' % obj.vartype)

    def write_obj_Mult(self, obj):
        """Turn a multvariable into a string""" 
        mult_list = [self.write_obj(factor) for factor in obj] 
        text = '(' 
        if obj.prefactor != 1:
            if obj.prefactor != -1:
                text = self.change_number_format(obj.prefactor) + '*' + text 
            else:
                text = '-' + text
        return text + '*'.join(mult_list) + ')'
    
    def write_obj_Add(self, obj):
        """Turns addvariable into a string"""
        mult_list = [self.write_obj(factor) for factor in obj]
        prefactor = ''
        if obj.prefactor == 1:
            prefactor = ''
        elif obj.prefactor == -1:
            prefactor = '-'
        else:
            prefactor = '%s*' % self.change_number_format(obj.prefactor)

        return '(%s %s)' % (prefactor, '+'.join(mult_list))

        
    def write_obj_Var(self, obj):
        text = ''
        if obj.prefactor != 1:
            if obj.prefactor != -1: 
                text = self.change_number_format(obj.prefactor) + '*' + text
            else:
                text = '-' + text
        text += self.change_var_format(obj.variable)
        if obj.power != 1:
            text = text + self.power_symbol + str(obj.power)
        return text

    def make_all_lists(self):
        """ Make all the list for call ordering, conservation impulsion, 
        basic declaration"""
        
        DeclareList = self.make_declaration_list()
        CallList = self.make_call_list()
        MomentumConserve = self.make_momentum_conservation()

        self.calllist =  {'CallList':CallList,'DeclareList':DeclareList, \
                           'Momentum':MomentumConserve}

    
    def make_call_list(self):
        """find the way to write the call of the functions"""

        # particle type counter
        nb_type = {'S':0, 'F':0, 'V':0, 'T':0}        
        call_arg = [] #incoming argument of the routine
        
        # update the type counter + make call_arg for amplitude
        for index,spin in enumerate(self.particles):
            nb_type[spin] += 1
            call_arg.append('%s%d' % (spin, index +1))
            
        # reorder call_arg if not amplitude
        if self.offshell:
            part_pos = self.offshell -1 
            out_type = self.particles[part_pos]
            
            #order is FVST #look at the border of the cycling move
            # start/stop are the index of the group of spin where to perform
            #cycling ordering.
            if out_type == 'F':
                start = 0
                stop = nb_type['F']
            elif out_type == 'V':
                start = nb_type['F']
                stop = start + nb_type['V']
            elif out_type == 'S':
                start = nb_type['F'] + nb_type['V']
                stop = start + nb_type['S']
            elif out_type == 'T':
                start = nb_type['F'] + nb_type['V']+ nb_type['S']
                stop = start + nb_type['T']
            else:
                raise NotImplemented, 'Only type FVST are supported' 
            
            #reorganize the order and suppress the output from this part
            call_arg = self.new_order(call_arg, part_pos, start, stop)
        
        return call_arg
            
    @ staticmethod
    def new_order(call_list, remove, start, stop):
        """ create the new order for the calling using cycling order"""
        
        assert(start <= remove <= stop <= len(call_list))
        
        new_list= call_list[:start]
        for i in range(remove+1, stop):
            new_list.append(call_list[i])
        for i in range(start, remove):
            new_list.append(call_list[i])
        new_list += call_list[stop:]
        
        return new_list
        
    def make_momentum_conservation(self):
        """ compute the sign for the momentum conservation """
        
        if not self.offshell:
            return []
        # How Convert  sign to a string
        sign_dict = {1: '+', -1: '-'}
        # help data 
        momentum_conserve = []
        nb_fermion =0
        
        #compute global sign
        if not self.offshell % 2 and self.particles[self.offshell -1] == 'F': 
            global_sign = 1
        else:
            global_sign = -1
        
        
        for index, spin in enumerate(self.particles): 
            assert(spin in ['S','F','V','T'])  
      
            #compute the sign
            if spin != 'F':
                sign = -1 * global_sign
            elif nb_fermion % 2 == 0:
                sign = global_sign
                nb_fermion += 1
            else: 
                sign = -1 * global_sign
                nb_fermion += 1
            
            # No need to include the outgoing particles in the definitions
            if index == self.offshell -1:
                continue 
            
            # write the
            momentum_conserve.append('%s%s%d' % (sign_dict[sign], spin, \
                                                                     index + 1))
        
        # Remove the
        if momentum_conserve[0][0] == '+':
            momentum_conserve[0] = momentum_conserve[0][1:]
        
        return momentum_conserve
    
    def make_declaration_list(self):
        """ make the list of declaration nedded by the header """
        
        declare_list = []
        for index, spin in enumerate(self.particles):
            # First define the size of the associate Object 
            declare_list.append(self.declare_dict[spin] % (index + 1) ) 
 
        return declare_list
 
    
        
class HelasWriterForFortran(WriteHelas): 
    """routines for writing out Fortran"""

    extension = '.f'
    declare_dict = {'S':'double complex S%d(3)',
                    'F':'double complex F%d(6)',
                    'V':'double complex V%d(6)',
                    'T':'double complex T%s(18)'}
    
    def define_header(self):
        """Define the Header of the fortran file. This include
            - function tag
            - definition of variable
        """
            
        Momenta = self.collected['momenta']
        Width = self.collected['width']
        Mass = self.collected['mass']
        OverM = self.collected['om']
        
        CallList = self.calllist['CallList']
        DeclareList = self.calllist['DeclareList']
        DeclareList.append('double complex C')
        
        local_declare = []
        OffShell = self.offshell
        OffShellParticle = OffShell -1 
        
        
        # define the type of function and argument
        if not OffShell:
            str_out = 'subroutine %(name)s(%(args)s,vertex)\n' % \
               {'name': self.namestring,
                'args': ','.join(CallList+ ['C'] + Mass + Width) } 
            local_declare.append('double complex vertex\n') 
        else: 
            local_declare.append('double complex denom\n')
            str_out = 'subroutine %(name)s(%(args)s, %(out)s%(number)d)\n' % \
               {'name': self.namestring,
                'args': ','.join(CallList+ ['C'] + Mass + Width), 
                'out': self.particles[OffShellParticle],
                'number': OffShellParticle + 1 
                }
                                 
        # Forcing implicit None
        str_out += 'implicit none \n'
        
        # Declare all the variable
        for elem in DeclareList + local_declare:
            str_out += elem + '\n'
        if len(Mass + Width) > 0:
            str_out += 'double precision ' + ','.join(Mass + Width) + '\n'
        if len(OverM) > 0: 
            str_out += 'double complex ' + ','.join(OverM) + '\n'
        if len(Momenta) > 0:
            str_out += 'double precision ' + '(0:3),'.join(Momenta) + '(0:3)\n'

        return str_out

            
    def define_momenta(self):
        """Define the Header of the fortran file. This include
            - momentum conservation
            -definition of the impulsion"""
        # Definition of the Momenta
        
        momenta = self.collected['momenta']
        overm = self.collected['om']
        momentum_conservation = self.calllist['Momentum']
        
        str_out = ''
        # Conservation of Energy Impulsion
        if self.offshell: 
            offshelltype = self.particles[self.offshell -1]
            offshell_size = self.type_to_size[offshelltype]            
            #Implement the conservation of Energy Impulsion
            for i in range(-1,1):
                str_out += '%s%d(%d)= ' % (offshelltype, self.offshell, \
                                                              offshell_size + i)
                
                pat=re.compile(r'^[-+]?(?P<spin>\w)')
                for elem in momentum_conservation:
                    spin = pat.search(elem).group('spin') 
                    str_out += '%s(%d)' % (elem, self.type_to_size[spin] + i)  
                str_out += '\n'  
                    
        # Momentum
        for mom in momenta:
            #Mom is in format PX with X the number of the particle
            index = int(mom[1:])
            
            type = self.particles[index - 1]
            energy_pos = self.type_to_size[type] -1
            sign = ''
            if self.offshell == index and (type == 'V' or type == 'S'):
                sign = '-'
                
            str_out += '%s(0) = %s dble(%s%d(%d))\n' % (mom, sign, type, index, energy_pos)
            str_out += '%s(1) = %s dble(%s%d(%d))\n' % (mom, sign, type, index, energy_pos + 1)
            str_out += '%s(2) = %s dimag(%s%d(%d))\n' % (mom, sign, type, index, energy_pos + 1)
            str_out += '%s(3) = %s dimag(%s%d(%d))\n' % (mom, sign, type, index, energy_pos)            
            
                   
        # Definition for the One Over Mass**2 terms
        for elem in overm:
            #Mom is in format OMX with X the number of the particle
            index = int(elem[2:])
            str_out += 'om%d = 0d0\n' % (index)
            str_out += 'if (m%d .ne. 0d0) om%d' % (index, index) + '=1d0/dcmplx(m%d**2,-w%d*m%d)\n' % (index, index, index) 
        
        # Returning result
        return str_out
        
        
    def change_var_format(self, name): 
        """Formatting the variable name to Fortran format"""
        
        if '_' in name:
            name = name.replace('_', '(', 1) + ')'
        #name = re.sub('\_(?P<num>\d+)$', '(\g<num>)', name)
        return name
    
    def change_number_format(self, number):
        """Formating the number"""
        if isinstance(number, complex):
            out = '(%.9fd0, %.9fd0)' % (number.real, number.imag)
        else:
            out = '%.9f' % number
        return out
    
    def define_expression(self):
        OutString = ''
        if not self.offshell:
            for ind in self.obj.listindices():
                string = 'Vertex = C*' + self.write_obj(self.obj.get_rep(ind))
                string = string.replace('+-', '-')
                string = re.sub('\((?P<num>[+-]*[0-9])(?P<num2>[+-][0-9])[Jj]\)\.', '(\g<num>d0,\g<num2>d0)', string)
                string = re.sub('(?P<num>[0-9])[Jj]\.', '\g<num>.*(0d0,1d0)', string)
                OutString = OutString + string + '\n'
        else:
            OffShellParticle = '%s%d' % (self.particles[self.offshell-1],\
                                                                  self.offshell)
            numerator = self.obj.numerator
            denominator = self.obj.denominator
            for ind in denominator.listindices():
                denom = self.write_obj(denominator.get_rep(ind))
            string = 'denom =' + '1d0/(' + denom + ')'
            string = string.replace('+-', '-')
            string = re.sub('\((?P<num>[+-]*[0-9])\+(?P<num2>[+-][0-9])[Jj]\)\.', '(\g<num>d0,\g<num2>d0)', string)
            string = re.sub('(?P<num>[0-9])[Jj]\.', '\g<num>*(0d0,1d0)', string)
            OutString = OutString + string + '\n'
            counter = 1
            for ind in numerator.listindices():
                string = '%s(%d)= C*denom*' % (OffShellParticle, counter)
                string += self.write_obj(numerator.get_rep(ind))
                string = string.replace('\+-', '-')
                string = re.sub('\((?P<num>[+-][0-9])\+(?P<num2>[+-][0-9])[Jj]\)\.', '(\g<num>d0,\g<num2>d0)', string)
                string = re.sub('(?P<num>[0-9])[Jj]\.', '\g<num>*(0d0,1d0)', string)
                OutString = OutString + string + '\n' 
                counter += 1
        return OutString 
    
    def define_symmetry(self):
        calls = self.calllist['CallList']
        number = self.offshell 
        Outstring = 'call '+self.namestring+'('+','.join(calls)+',C,M%s,W%s,%s%s)' \
                         %(number,number,self.particles[self.offshell-1],number)
        return Outstring
    
    def define_foot(self):
        return 'end' 

    def write(self):
                
        writer = writers.FortranWriter(self.out_path)
        writer.downcase = False 
        commentstring = 'This File is Automatically generated by ALOHA \n'
        commentstring += 'The process calculated in this file is: \n'
        commentstring += self.comment + '\n'
        writer.write_comments(commentstring)
         
        # write head - momenta - body - foot
        writer.writelines(self.define_header())
        writer.writelines(self.define_momenta())
        writer.writelines(self.define_expression())
        writer.writelines(self.define_foot())
        
        for elem in self.symmetries: 
            symmetryhead = self.define_header().replace( \
                             self.namestring,self.namestring[0:-1]+'%s' %(elem))
            symmetrybody = self.define_symmetry()
            writer.write_comments('\n%s\n' % ('#'*65))
            writer.writelines(symmetryhead)
            writer.writelines(symmetrybody)
            writer.writelines(self.define_foot())
        
def get_helas_name(name,outgoing):
    """ build the name of the helas function """
    
    return '%s_%s' % (name, outgoing) 

class HelasWriterForCPP(WriteHelas): 
    """routines for writing out Fortran"""
    
    declare_dict = {'S':'double complex S%d[3]',
                    'F':'double complex F%d[6]',
                    'V':'double complex V%d[6]',
                    'T':'double complex T%s[18]'}
    
    def define_header(self):
        """Define the Header of the fortran file. This include
            - function tag
            - definition of variable
            - momentum conservation
        """
            
        Momenta = self.collected['momenta']
        Width = self.collected['width']
        Mass = self.collected['mass']
        OverM = self.collected['om']
        
        CallList = self.calllist['CallList']
        DeclareList = self.calllist['DeclareList']
        DeclareList.append('double complex C')
        
        local_declare = []
        OffShell = self.offshell
        OffShellParticle = OffShell -1 
        # Transform function call variables to C++ format
        for i, call in enumerate(CallList):
            CallList[i] = "complex<double> %s[]" % call
        if Mass:
            Mass[0] = "double %s" % Mass[0]
        if Width:
            Width[0] = "double %s" % Width[0]
        
        # define the type of function and argument
        if not OffShell:
            str_out = 'void %(name)s(%(args)s, complex<double> vertex)' % \
               {'name': self.namestring,
                'args': ','.join(CallList + ['complex<double> C'] + Mass + Width)}
        else: 
            local_declare.append('complex<double> denom;\n')
            str_out = 'void %(name)s(%(args)s, complex<double>%(out)s%(number)d[])' % \
              {'name': self.namestring,
               'args': ','.join(CallList+ ['complex<double> C'] + Mass + Width),
               'out': self.particles[OffShellParticle],
               'number': OffShellParticle + 1 
               }

        h_string = str_out + ";\n\n"
        cc_string = str_out + "{\n"
        # Declare all the variable
        for elem in local_declare:
            cc_string += elem + '\n'
        if len(OverM) > 0: 
            cc_string += 'complex<double> %s;\n' % ','.join(OverM)
        if len(Momenta) > 0:
            cc_string += 'double %s[4];\n' % '[4],'.join(Momenta)

        return {'h_header': h_string, 'cc_header': cc_string}
            
    def define_momenta(self):
        """Write the expressions for the momentum of the outgoing
        particle."""

        momenta = self.collected['momenta']
        overm = self.collected['om']
        momentum_conservation = self.calllist['Momentum']
        
        str_out = ''
        # Energy
        if self.offshell: 
            offshelltype = self.particles[self.offshell -1]
            offshell_size = self.type_to_size[offshelltype]            
            #Implement the conservation of Energy Impulsion
            for i in range(-2,0):
                str_out += '%s%d[%d]= ' % (offshelltype, self.offshell,
                                           offshell_size + i)
                
                pat=re.compile(r'^[-+]?(?P<spin>\w)')
                for elem in momentum_conservation:
                    spin = pat.search(elem).group('spin') 
                    str_out += '%s[%d]' % (elem, self.type_to_size[spin] + i)  
                str_out += ';\n'
        
        # Momentum
        for mom in momenta:
            #Mom is in format PX with X the number of the particle
            index = int(mom[1:])
            
            type = self.particles[index - 1]
            energy_pos = self.type_to_size[type] -1
            sign = ''
            if self.offshell == index and (type == 'V' or type == 'S'):
                sign = '-'
                
            str_out += '%s[0] = %s%s%d[%d].real();\n' % (mom, sign, type, index, energy_pos)
            str_out += '%s[1] = %s%s%d[%d].real();\n' % (mom, sign, type, index, energy_pos + 1)
            str_out += '%s[2] = %s%s%d[%d].imag();\n' % (mom, sign, type, index, energy_pos + 1)
            str_out += '%s[3] = %s%s%d[%d].imag();\n' % (mom, sign, type, index, energy_pos)            
            
                   
        # Definition for the One Over Mass**2 terms
        for elem in overm:
            #Mom is in format OMX with X the number of the particle
            index = int(elem[2:])
            str_out += 'OM%d = 0;\n' % (index)
            str_out += 'if (M%d != 0) OM%d' % (index, index) + '= 1./complex<double>(pow(M%d,2),-W%d*M%d);\n' % (index, index, index) 
        
        # Returning result
        return str_out
        
        
    def change_var_format(self, name): 
        """Formatting the variable name to C++ format"""
        
        if '_' in name:
            name = name.replace('_','[',1) +']'
        outstring = ''
        counter = 0
        for elem in re.finditer('[FVTSfvts][0-9]\[[0-9]\]',name):
            outstring += name[counter:elem.start()+2]+'['+str(int(name[elem.start()+3:elem.start()+4])-1)+']'
            counter = elem.end()
        outstring += name[counter:]
        #name = re.sub('\_(?P<num>\d+)$', '(\g<num>)', name)
        return outstring
    
    def change_number_format(self, number):
        """Formating the number"""
        if isinstance(number, complex):
            if number.real == int(number.real) and \
                   number.imag == int(number.imag):
                out = 'complex<double>(%d., %d.)' % \
                      (int(number.real), int(number.imag))
            else:
                out = 'complex<double>(%.9f, %.9f)' % \
                      (number.real, number.imag)                
        else:
            if number == int(number):
                out = '%d.' % int(number)
            else:
                out = '%.9f' % number
        return out
    
    def define_expression(self):
        OutString = '' 
        if not self.offshell:
            for ind in self.obj.listindices():
                string = 'vertex = C*' + self.write_obj(self.obj.get_rep(ind))
                string = string.replace('+-', '-')
                OutString = OutString + string + ';\n'
        else:
            OffShellParticle = self.particles[self.offshell-1]+'%s'%(self.offshell)
            numerator = self.obj.numerator
            denominator = self.obj.denominator
            for ind in denominator.listindices():
                denom = self.write_obj(denominator.get_rep(ind))
            string = 'denom =' + '1./(' + denom + ')'
            string = string.replace('+-', '-')
            OutString = OutString + string + ';\n'
            counter = 0
            for ind in numerator.listindices():
                string = '%s[%d]= C*denom*' % (OffShellParticle, counter)
                string += self.write_obj(numerator.get_rep(ind))
                string = string.replace('+-', '-')
                OutString = OutString + string + ';\n' 
                counter += 1
        OutString = re.sub('(?P<variable>[A-Za-z]+[0-9]\[*[0-9]*\]*)\*\*(?P<num>[0-9])','pow(\g<variable>,\g<num>)',OutString)
        return OutString 

    
    def define_symmetry(self):
        calls = self.calllist['CallList']
        number = self.offshell 
        Outstring = self.namestring+'('+','.join(calls)+',complex<double> C,double M%s,double W%s,complex<double>%s%s[])' \
                         %(number,number,self.particles[self.offshell-1],number)
        return Outstring
    
    def define_foot(self):
        """Return the end of the function definition"""

        return '}' 

    def write_h(self, header):
        """Return the full contents of the .h file"""

        h_string = '#ifndef '+ self.namestring + '_guard\n'
        h_string += '#define ' + self.namestring + '_guard\n'
        h_string += '#include <complex>\n'
        h_string += 'using namespace std;\n\n'

        h_header = header['h_header']

        h_string += h_header

        for elem in self.symmetries: 
            symmetryhead = h_header.replace( \
                             self.namestring,self.namestring[0:-1]+'%s' %(elem))
            h_string += ('//\n//%s\n' % ('#'*65))
            h_string += symmetryhead

        h_string += '#endif'

        return h_string

    def write_cc(self, header):
        """Return the full contents of the .cc file"""

        cc_string = '#include \"%s.h\"\n\n' % self.namestring
        cc_header = header['cc_header']
        cc_header += self.define_momenta()
        cc_header += self.define_expression()
        cc_header += self.define_foot()

        for elem in self.symmetries: 
            symmetryhead = cc_header.replace( \
                             self.namestring,self.namestring[0:-1]+'%s' %(elem))
            symmetrybody = self.define_symmetry()
            cc_header += '//\n//%s\n' % ('#'*65)
            cc_header += symmetryhead
            cc_header += symmetrybody
            cc_header += self.define_foot()

        return cc_header
    
    def write(self):
        writer_h = writers.CPPWriter(self.out_path + ".h")
        writer_cc = writers.CPPWriter(self.out_path + ".cc")
        commentstring = 'This File is Automatically generated by ALOHA \n'
        commentstring += 'The process calculated in this file is: \n'
        commentstring += self.comment + '\n'
        writer_h.write_comments(commentstring)
        writer_cc.write_comments(commentstring)
         
        # write head - momenta - body - foot
        
        header = self.define_header()
        writer_h.writelines(self.write_h(header))
        writer_cc.writelines(self.write_cc(header))
        
