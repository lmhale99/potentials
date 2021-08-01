# Standard libraries
import uuid

from DataModelDict import DataModelDict as DM

from ...tools import aslist
from ...record import PotentialLAMMPS
from ...record.Artifact import Artifact

class PotentialLAMMPSBuilder(object):
    """
    Template class for generating potential_LAMMPS records for different pair styles.

    Note: terms for pair_coeff lines are not included as they are style-specific.
    """

    def __init__(self, id=None, key=None, potid=None, potkey=None,
                 units=None, atom_style=None, pair_style=None,
                 pair_style_terms=None, status='active', comments=None, dois=None,
                 allsymbols=False, elements=None, masses=None, charges=None,
                 symbols=None, command_terms=None, artifacts=None):
        """
        Builder class initializer.
        
        Parameters
        ----------
        id : str, optional
            A human-readable identifier to name the LAMMPS potential
            implementation.  Must be set in order to save to the database as
            the id is used as the potential's file name.
        key : str, optional
            A UUID4 code to uniquely identify the LAMMPS potential
            implementation.  If not specified, a new UUID4 code is
            automatically generated.
        potid : str, optional
            A human-readable identifier to refer to the conceptual potential
            model that the potential is based on.  This should be shared by
            alternate implementations of the same potential.
        potkey : str, optional
            A UUID4 code to uniquely identify the conceptual potential model.
            This should be shared by alternate implementations of the same
            potential. If not specified, a new UUID4 code is automatically
            generated.
        units : str, optional
            The LAMMPS units option to use.
        atom_style : str, optional
            The LAMMPS atom_style option to use.
        pair_style : str, optional
            The LAMMPS pair_style option to use.
        pair_style_terms :  list, optional
            Any other terms that appear on the pair_style line (like cutoff)
            if needed.
        status : str, optional
            Indicates if the implementation is 'active' (valid and current),
            'superseded' (valid, but better ones exist), or 'retracted'
            (invalid). Default value is 'active'.
        comments : str, optional
            Descriptive information about the potential.
        dois : str or list, optional
            Any DOIs associated with the potential.
        allsymbols : bool, optional
            Flag indicating if the coefficient lines must be defined for every
            particle model in the potential even if those particles are not
            used.  Default value is False as most pair_styles do not require
            this.
        elements : str or list, optional
            The elemental symbols associated with each particle model if the
            particles represent atoms.
        masses : float or list, optional
            The masses of each particle.  Optional if elements is given as
            standard values can be used.
        charges : float or list, optional
            The static charges to assign to each particle, if the model calls
            for it.
        symbols : str or list, optional
            The symbols used to identify each unique particle model. Optional
            if elements is given and the particle symbols are the same as the
            elemental symbols.
        command_terms : list, optional
            Allows any other LAMMPS command lines that must be set for the
            potential to work properly to be set.  Each command line should be
            given as a list of terms, and multiple command lines given as a
            list of lists.
        artifacts : potential.Artifact or list, optional
            Artifact objects detailing any associated parameter or data files
            and the URLs where they can be downloaded from.
        """
        self.id = id
        self.key = key
        self.potid = potid
        self.potkey = potkey
        
        self.units = units
        self.atom_style = atom_style
        self.pair_style = pair_style
        
        self.allsymbols = allsymbols
        self.status = status
        self.comments = comments
        self.dois = dois

        self.symbols = symbols
        self.elements = elements
        self.masses = masses
        self.charges = charges
        
        self.pair_style_terms = pair_style_terms
        self.command_terms = command_terms

        self.artifacts = artifacts

    @property
    def id(self):
        """Human-readable id for LAMMPS implementation of the potential."""
        return self.__id

    @id.setter
    def id(self, value):
        if value is not None:
            value = str(value)
        self.__id = value

    @property
    def key(self):
        """Unique UUID4 key for the LAMMPS implementation."""
        return self.__key

    @key.setter
    def key(self, value):
        if value is None:
            value = uuid.uuid4()
        self.__key = str(value)

    @property
    def potid(self):
        """Human-readable id for the potential model."""
        return self.__potid

    @potid.setter
    def potid(self, value):
        if value is not None:
            value = str(value)
        self.__potid = value

    @property
    def potkey(self):
        """Unique UUID4 key for the potential model."""
        return self.__potkey

    @potkey.setter
    def potkey(self, value):
        if value is None:
            value = uuid.uuid4()
        self.__potkey = str(value)

    @property
    def units(self):
        """str : LAMMPS units option."""
        return self.__units

    @units.setter
    def units(self, value):
        if value is not None:
            value = str(value)
        self.__units = value

    @property
    def atom_style(self):
        """str : LAMMPS atom_style option."""
        return self.__atom_style

    @atom_style.setter
    def atom_style(self, value):
        if value is not None:
            value = str(value)
        self.__atom_style = value

    @property
    def pair_style(self):
        """str : LAMMPS pair_style option."""
        return self.__pair_style

    @pair_style.setter
    def pair_style(self, value):
        if value is not None:
            value = str(value)
        self.__pair_style = value

    @property
    def allsymbols(self):
        """bool : Flag indicating if the coefficient lines must be defined for every particle model in the potential even if those particles are not used."""
        return self.__allsymbols

    @allsymbols.setter
    def allsymbols(self, value):
        if isinstance(value, bool):
            self.__allsymbols = value
        elif value.lower() == 'true':
            self.__allsymbols = True
        elif value.lower() == 'false':
            self.__allsymbols = False
        else:
            raise ValueError(f'Invalid allsymbols value "{value}"')

    @property
    def status(self):
        """str : The status of the LAMMPS potential: active, superseded or retracted"""
        return self.__status

    @status.setter
    def status(self, value):
        if value not in ['active', 'superseded', 'retracted']:
            raise ValueError('Invalid status: allowed values are active, superseded, and retracted')
        self.__status = value

    @property
    def comments(self):
        """str : Descriptive information about the potential"""
        return self.__comments

    @comments.setter
    def comments(self, value):
        if value is not None:
            value = str(value)
        self.__comments = value

    @property
    def dois(self):
        """list : Any DOIs associated with the potential"""
        return self.__dois

    @dois.setter
    def dois(self, value):
        if value is not None:
            self.__dois = aslist(value)
        else:
            self.__dois = []

    @property
    def symbols(self):
        """list : The interaction models defined by the potential"""
        return self.__symbols

    @symbols.setter
    def symbols(self, value):
        if value is not None:
            value = aslist(value)
        self.__symbols = value

    @property
    def elements(self):
        """list : The elements associated with each interaction model"""
        return self.__elements

    @elements.setter
    def elements(self, value):
        if value is not None:
            value = aslist(value)
        self.__elements = value

    @property
    def masses(self):
        """list : The atomic or particle mass associated with each interaction model"""
        return self.__masses

    @masses.setter
    def masses(self, value):
        if value is not None:
            value = aslist(value)
        self.__masses = value

    @property
    def charges(self):
        """list : The atomic or particle charge associated with each interaction model"""
        return self.__charges

    @charges.setter
    def charges(self, value):
        if value is not None:
            value = aslist(value)
        self.__charges = value

    @property
    def pair_style_terms(self):
        """list : All extra terms to include in the pair_style command line"""
        return self.__pair_style_terms

    @pair_style_terms.setter
    def pair_style_terms(self, value):
        if value is not None:
            self.__pair_style_terms = aslist(value)
        else:
            self.__pair_style_terms = []

    @property
    def command_terms(self):
        """list : All extra command lines to include"""
        return self.__command_terms

    @command_terms.setter
    def command_terms(self, value):
        if value is not None:
            value = aslist(value)
            if not isinstance(value[0], list):
                value = [value]
            self.__command_terms = value
        else:
            self.__command_terms = []

    @property
    def artifacts(self):
        return self.__artifacts

    @artifacts.setter
    def artifacts(self, value):
        self.__artifacts = []
        if value is not None:
            value = aslist(value)
            for v in value:
                if isinstance(v, Artifact):
                    self.__artifacts.append(v)
                elif isinstance(v, dict):
                    self.add_artifact(**v)
                else:
                    raise TypeError('Invalid artifact object: must be an Artifact or dict')

    def build(self):
        """
        Generates a PotentialLAMMPS data model using the given parameters.

        Returns
        -------
        DataModelDict
            The PotentialLAMMPS data model.
            
        Raises
        ValueError
            If elements and/or symbols not set, if masses not set when elements
            are not given, or if pair_style is not set.
        """
        # Check that required values have been set
        if self.symbols is None and self.elements is None:
            raise ValueError('elements and/or symbols must be set')
        if self.elements is None and self.masses is None:
            raise ValueError('masses must be set if elements are not given')
        if self.pair_style is None:
            raise ValueError('pair_style must be set')

        # Initialize model
        model = DM()
        model['potential-LAMMPS'] = DM()
        model['potential-LAMMPS']['key'] = self.key
        model['potential-LAMMPS']['id'] = self.id
        if self.status != 'active':
            model['potential-LAMMPS']['status'] = self.status
        
        model['potential-LAMMPS']['potential'] = DM()
        model['potential-LAMMPS']['potential']['key'] = self.potkey
        model['potential-LAMMPS']['potential']['id'] = self.potid
        for doi in self.dois:
            model['potential-LAMMPS']['potential'].append('doi', doi)

        if self.comments is not None:
            model['potential-LAMMPS']['comments'] = self.comments
        model['potential-LAMMPS']['units'] = self.units
        model['potential-LAMMPS']['atom_style'] = self.atom_style
        if self.allsymbols is True:
            model['potential-LAMMPS']['allsymbols'] = True

        # Add list of atoms
        for atom in self.iteratoms():
            model['potential-LAMMPS'].append('atom', atom)
        
        # Add pair style and coeff terms
        model['potential-LAMMPS']['pair_style'] = self.buildpairstyle()
        model['potential-LAMMPS']['pair_coeff'] = self.buildpaircoeff()
        
        # Add any extra command lines
        for command in self.buildcommands():
            model['potential-LAMMPS'].append('command', command)

        # Add artifacts
        for artifact in self.artifacts:
            model['potential-LAMMPS'].append('artifact', artifact.build_model()['artifact'])

        return model

    def potential(self, pot_dir=None):
        return PotentialLAMMPS(self.build(), pot_dir=pot_dir)

    @property
    def supported_pair_styles(self):
        """tuple : The list of known pair styles that use this format."""
        return ()

    @property
    def symbollist(self):
        """The list of all of the model symbols defined by the potential"""
        if self.symbols is not None:
            return ' '.join(self.symbols)
        else:
            return ' '.join(self.elements)

    def iteratoms(self):
        """
        Iterates through the list of atoms with fields element, symbol, mass, charge
        """
        if self.symbols is not None:
            symbols = self.symbols
        else:
            symbols = [None for i in range(len(self.elements))]
        
        if self.elements is not None:
            elements = self.elements
        else:
            elements = [None for i in range(len(self.symbols))]
        
        if self.masses is not None:
            masses = self.masses
        else:
            masses = [None for i in range(len(elements))]

        if self.charges is not None:
            charges = self.charges
        else:
            charges = [None for i in range(len(elements))]

        assert len(symbols) == len(elements), 'incompatible symbols, elements lengths'
        assert len(symbols) == len(masses), 'incompatible symbols, masses lengths'
        assert len(symbols) == len(charges), 'incompatible symbols, charges lengths'

        for element, symbol, mass, charge in zip(elements, symbols, masses, charges):
            atom = DM()
            if symbol is not None:
                atom['symbol'] = symbol
            if element is not None:
                atom['element'] = element
            if mass is not None:
                atom['mass'] = mass
            if charge is not None:
                atom['charge'] = charge
            yield atom

    def buildpairstyle(self):
        """Builds the pair_style command line"""
        pairstyle = DM()
        pairstyle['type'] = self.pair_style
        
        for term in self.pair_style_terms:
            if isinstance(term, (int, float)):
                pairstyle.append('term', DM([('parameter', term)]))
            else:
                pairstyle.append('term', DM([('option', str(term))]))
        return pairstyle

    def buildpaircoeff(self):
        """Builds the pair_coeff command lines"""
        paircoeff = None

        return paircoeff

    def buildcommands(self):
        """Builds extra command lines from command_terms"""
        commands = []
        for line in self.command_terms:
            if len(line) == 0:
                continue
            command = DM()
            for term in line:
                if isinstance(term, (int, float)):
                    command.append('term', DM([('parameter', term)]))
                else:
                    command.append('term', DM([('option', str(term))]))
            commands.append(command)
        return commands

    def add_artifact(self, model=None, filename=None, label=None, url=None):
        self.artifacts.append(Artifact(model=model, filename=filename, label=label, url=url))