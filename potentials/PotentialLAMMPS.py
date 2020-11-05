# coding: utf-8
# Standard Python libraries
from pathlib import Path

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# atomman imports
from .tools import atomic_mass, aslist, uber_open_rmode

class PotentialLAMMPS(object):
    """
    Class for building LAMMPS input lines from a potential-LAMMPS data model.
    """
    
    def __init__(self, model, pot_dir=None):
        """
        Initializes an instance associated with a potential-LAMMPS data model.
        
        Parameters
        ----------
        model : str or file-like object
            A JSON/XML data model containing a potential-LAMMPS branch.
        pot_dir : str, optional
            The path to a directory containing any artifacts associated with
            the potential.  Default value is None, which assumes any required
            files will be in the working directory when LAMMPS is executed.
        """
        self.load(model, pot_dir)
    
    def load(self, model, pot_dir=None):
        """
        Loads potential-LAMMPS data model info.
        
        Parameters
        ----------
        model : str or file-like object
            A JSON/XML data model containing a potential-LAMMPS branch.
        pot_dir : str, optional
            The path to a directory containing any artifacts associated with
            the potential.  Default value is None, which assumes any required
            files will be in the working directory when LAMMPS is executed.
        """
        
        # Load model and find potential-LAMMPS
        self.__dm = DM(model).find('potential-LAMMPS')
        
        # Extract properties
        self.__id = self.__dm['id']
        self.__key = self.__dm['key']
        self.__potid = self.__dm['potential']['id']
        self.__potkey = self.__dm['potential']['key']
        self.__units = self.__dm['units']
        self.__atom_style = self.__dm['atom_style']
        self.__pair_style = self.__dm['pair_style']['type']

        allsymbols = self.__dm.get('allsymbols', 'False')
        if allsymbols is True or allsymbols.lower() == 'true':
            self.__allsymbols = True
        elif allsymbols is False or allsymbols.lower() == 'false':
            self.__allsymbols = False
        else:
            raise ValueError(f'Invalid allsymbols value "{allsymbols}"')
        
        self.__status = self.__dm.get('status', 'active')

        if pot_dir is not None:
            self.pot_dir = pot_dir
        else:
            self.pot_dir = ''
        
        # Build lists of symbols, elements and masses
        self.__elements = []
        self.__symbols = []
        self.__masses = []
        self.__charges = []
        for atom in self.__dm.iteraslist('atom'):
            element = atom.get('element', None)
            symbol = atom.get('symbol', None)
            mass = atom.get('mass', None)
            charge = float(atom.get('charge', 0.0))
            
            # Check if element is listed
            if element is None:
                if mass is None:
                    raise KeyError('mass is required for each atom if element is not listed')
                if symbol is None:
                    raise KeyError('symbol is required for each atom if element is not listed')
                else:
                    element = symbol
            
            # Check if symbol is listed.
            if symbol is None:
                symbol = element
            
            # Check if mass is listed.
            if mass is None:
                mass = atomic_mass(element)
            else:
                mass = float(mass)
            
            # Add values to the lists
            self.__elements.append(element)
            self.__symbols.append(symbol)
            self.__masses.append(mass)
            self.__charges.append(charge)
        
    def normalize_symbols(self, symbols):
        """
        Modifies a given list of symbols to be compatible with the potential.
        Mostly, this converts symbols to a list if it is not already one, and
        adds additional symbols if the potential's allsymbols setting is True.

        Parameters
        ----------
        symbols : str or list-like object
            The initial list of symbols
        
        Returns
        -------
        list
            The updated list.
        """
        
        # Convert symbols to a list if needed
        symbols = aslist(symbols)
        
        # Check that all symbols are set
        for symbol in symbols:
            assert symbol is not None, 'symbols list incomplete: found None value'
        
        # Add missing symbols if potential's allsymbols is True
        if self.allsymbols:
            for symbol in self.symbols:
                if symbol not in symbols:
                    symbols.append(symbol)
        
        return symbols
    
    def __str__(self):
        """str: The string of the Potential returns its human-readable id"""
        return self.id
    
    @property
    def pot_dir(self):
        """str : The directory containing files associated with a given potential."""
        return self.__pot_dir
    
    @pot_dir.setter
    def pot_dir(self, value):
        self.__pot_dir = str(value)
    
    @property
    def id(self):
        """str : Human-readable identifier for the LAMMPS implementation."""
        return self.__id
    
    @property
    def key(self):
        """str : uuid hash-key for the LAMMPS implementation."""
        return self.__key
    
    @property
    def potid(self):
        """str : Human-readable identifier for the potential model."""
        return self.__potid
    
    @property
    def potkey(self):
        """str : uuid hash-key for the potential model."""
        return self.__potkey
    
    @property
    def units(self):
        """str : LAMMPS units option."""
        return self.__units
    
    @property
    def atom_style(self):
        """str : LAMMPS atom_style option."""
        return self.__atom_style
    
    @property
    def symbols(self):
        """list of str : All atom-model symbols."""
        return self.__symbols
    
    @property
    def pair_style(self):
        return self.__pair_style
    
    @property
    def allsymbols(self):
        """bool : indicates if all model symbols must be listed."""
        return self.__allsymbols

    @property
    def status(self):
        """str : Indicates the status of the implementation (active, superseded, retracted)"""
        return self.__status

    @property
    def model(self):
        return self.__dm

    def elements(self, symbols=None):
        """
        Returns a list of element names associated with atom-model symbols.
        
        Parameters
        ----------
        symbols : list of str, optional
            A list of atom-model symbols.  If None (default), will use all of
            the potential's symbols.
        
        Returns
        -------
        list of str
            The str element symbols corresponding to the atom-model symbols.
        """
        # Return all elements if symbols is None
        if symbols is None:
            return self.__elements
        
        # Normalize symbols
        symbols = self.normalize_symbols(symbols)
        
        # Get all matching elements
        elements = []
        for symbol in symbols:
            i = self.symbols.index(symbol)
            elements.append(self.__elements[i])
        
        return elements
        
    def masses(self, symbols=None):
        """
        Returns a list of atomic/ionic masses associated with atom-model
        symbols.
        
        Parameters
        ----------
        symbols : list of str, optional
            A list of atom-model symbols.  If None (default), will use all of
            the potential's symbols.
        
        Returns
        -------
        list of float
            The atomic/ionic masses corresponding to the atom-model symbols.
        """
        # Return all masses if symbols is None
        if symbols is None:
            return self.__masses
        
        # Normalize symbols
        symbols = self.normalize_symbols(symbols)
        
        # Get all matching masses
        masses = []
        for symbol in symbols:
            i = self.symbols.index(symbol)
            masses.append(self.__masses[i])
        
        return masses

    def charges(self, symbols=None):
        """
        Returns a list of atomic charges associated with atom-model symbols.
        Will have a None value if not assigned.
        
        Parameters
        ----------
        symbols : list of str, optional
            A list of atom-model symbols.  If None (default), will use all of
            the potential's symbols.
        
        Returns
        -------
        list of float
            The atomic charges corresponding to the atom-model symbols.
        """
        # Return all charges if symbols is None
        if symbols is None:
            return self.__charges
        
        # Normalize symbols
        symbols = self.normalize_symbols(symbols)
        
        # Get all matching charges
        charges = []
        for symbol in symbols:
            i = self.symbols.index(symbol)
            charges.append(self.__charges[i])
        
        return charges

    def asdict(self):
        """Returns a flat dict of the metadata fields"""
        d = {}
        d['id'] = self.id
        d['key'] = self.key
        d['potid'] = self.potid
        d['potkey'] = self.potkey
        d['units'] = self.units
        d['atom_style'] = self.atom_style
        d['allsymbols'] = self.allsymbols
        d['pair_style'] = self.pair_style
        d['status'] = self.status
        d['symbols'] = self.symbols
        d['elements'] = self.elements()
        d['masses'] = self.masses()
        d['charges'] = self.charges()

        return d

    def asmodel(self):
        return DM([('potential-LAMMPS', self.__dm)])

    def pair_info(self, symbols=None, masses=None):
        """
        Generates the LAMMPS input command lines associated with the Potential
        and a list of atom-model symbols.
        
        Parameters
        ----------
        symbols : list of str, optional
            List of atom-model symbols corresponding to the atom types in a
            system.  If None (default), then all atom-model symbols will
            be included in the order that they are listed in the data model.
        masses : list, optional
            Can be given to override the default symbol-based masses for each
            atom type.  Must be a list of the same length as symbols.  Any
            values of None in the list indicate that the default value be used
            for that atom type.
        
        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential.
        """
        if self.pair_style == 'kim':
            return self.__pair_info_kim(symbols=symbols, masses=masses)

        # If no symbols supplied use all for potential
        if symbols is None:
            symbols = self.symbols
        else:
            symbols = aslist(symbols)

        # Check length of masses
        if masses is not None:
            masses = aslist(masses)
            assert len(masses) == len(symbols), 'supplied masses must be same length as symbols'
        
        # Normalize symbols
        symbols = self.normalize_symbols(symbols)
        
        # Set masses
        defaultmasses = self.masses(symbols)
        if masses is not None:
            for i in range(len(masses)):
                if masses[i] is not None:
                    defaultmasses[i] = masses[i]
        masses = defaultmasses
        
        info = ''

        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'
        
        # Generate pair_style line
        terms = self.__dm['pair_style'].aslist('term')
        style_terms = self.__pair_terms(terms)
        
        info += f'pair_style {self.pair_style}{style_terms}\n'
        
        # Generate pair_coeff lines
        for coeff_line in self.__dm.iteraslist('pair_coeff'):
            if 'interaction' in coeff_line:
                interaction = coeff_line['interaction'].get('symbol', ['*', '*'])
            else:
                interaction = ['*', '*']
            
            # Always include coeff lines that act on all atoms in the system
            if interaction == ['*', '*']:
                coeff_symbols = self.symbols
                coeff_terms = self.__pair_terms(coeff_line.iteraslist('term'),
                                                symbols, coeff_symbols)
                
                info += f'pair_coeff * *{coeff_terms}\n'
                continue
            
            # Many-body potentials will contain a symbols term
            if len(coeff_line.finds('symbols')) > 0:
                many = True
            else:
                many = False
            
            # Treat as a many-body potential
            if many:
                coeff_symbols = interaction
                coeff_terms = self.__pair_terms(coeff_line.iteraslist('term'),
                                           symbols, coeff_symbols) + '\n'
                
                info += f'pair_coeff * *{coeff_terms}\n' 
            
            # Treat as pair potential
            else:
                coeff_symbols = interaction
                if len(coeff_symbols) != 2:
                    raise ValueError('Pair potential interactions need two listed elements')
                
                # Classic eam style is a special case
                if self.pair_style == 'eam':
                    if coeff_symbols[0] != coeff_symbols[1]:
                        raise ValueError('Only i==j interactions allowed for eam style')
                    for i in range(len(symbols)):
                        if symbols[i] == coeff_symbols[0]:
                            coeff_terms = self.__pair_terms(coeff_line.iteraslist('term'),
                                                           symbols, coeff_symbols)
                            
                            info += f'pair_coeff {i+1} {i+1}{coeff_terms}\n'
                
                # All other pair potentials
                else:
                    for i in range(len(symbols)):
                        for j in range(i, len(symbols)):
                            if ((symbols[i] == coeff_symbols[0] and symbols[j] == coeff_symbols[1])
                             or (symbols[i] == coeff_symbols[1] and symbols[j] == coeff_symbols[0])):
                                coeff_terms = self.__pair_terms(coeff_line.iteraslist('term'),
                                                                symbols, coeff_symbols)
                                
                                info += f'pair_coeff {i+1} {j+1}{coeff_terms}\n'
        
        # Generate additional command lines
        for command_line in self.__dm.iteraslist('command'):
            info += self.__pair_terms(command_line.iteraslist('term'),
                                         symbols, self.symbols).strip() + '\n'
        
        return info
    
    def __pair_terms(self, terms, system_symbols=None, coeff_symbols=None):
        """utility function used by self.pair_info() for composing lines from terms"""
        if system_symbols is None:
            system_symbols = []
        if coeff_symbols is None:
            coeff_symbols = []
        
        line = ''
        
        for term in terms:
            for ttype, tval in term.items():
                
                # Print options and parameters as strings
                if ttype == 'option' or ttype == 'parameter':
                    line += ' ' + str(tval)
                
                # Print files with pot_dir prefixes
                elif ttype == 'file':
                    line += ' ' + str(Path(self.pot_dir, tval))
                
                # Print all symbols being used for symbolsList
                elif ttype == 'symbolsList' and (tval is True or tval.lower() == 'true'):
                    for coeff_symbol in coeff_symbols:
                        if coeff_symbol in system_symbols:
                            line += ' ' + coeff_symbol
                
                # Print symbols being used with model in appropriate order for symbols
                elif ttype == 'symbols' and (tval is True or tval.lower() == 'true'):
                    for system_symbol in system_symbols:
                        if system_symbol in coeff_symbols:
                            line += ' ' + system_symbol
                        else:
                            line += ' NULL'
        
        return line

    def __pair_info_kim(self, symbols=None, masses=None):
        """
        Generates the LAMMPS input command lines associated with a KIM
        Potential and a list of atom-model symbols.
        
        Parameters
        ----------
        symbols : list of str, optional
            List of atom-model symbols corresponding to the atom types in a
            system.  If None (default), then all atom-model symbols will
            be included in the order that they are listed in the data model.
        masses : list, optional
            Can be given to override the default symbol-based masses for each
            atom type.  Must be a list of the same length as symbols.  Any
            values of None in the list indicate that the default value be used
            for that atom type.
        
        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential.
        """
        # If no symbols supplied use all for potential
        if symbols is None:
            symbols = self.symbols
        else:
            symbols = aslist(symbols)

        # Check length of masses
        if masses is not None:
            masses = aslist(masses)
            assert len(masses) == len(symbols), 'supplied masses must be same length as symbols'
        
        # Normalize symbols
        symbols = self.normalize_symbols(symbols)
        
        # Set masses
        defaultmasses = self.masses(symbols)
        if masses is not None:
            for i in range(len(masses)):
                if masses[i] is not None:
                    defaultmasses[i] = masses[i]
        masses = defaultmasses
        
        # Generate kim_init line
        info = f'kim_init {self.id} {self.units}\n'
        
        # Generate kim_interactions  line
        info += f'kim_interactions {" ".join(symbols)}\n'
        
        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'

        return info