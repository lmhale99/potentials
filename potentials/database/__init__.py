# coding: utf-8

from cdcs import CDCS

class Database():
    """
    Class for interacting with potential records hosted from potentials.nist.gov
    """
    # Class imports
    from ._citation import (citations, citations_df, load_citations,
                            get_citation, _no_load_citations, copy_citations,
                            save_citation)
    from ._potential import (potentials, potentials_df, load_potentials,
                             copy_potentials, save_potential,
                             get_potential, get_potentials, _no_load_potentials)
    from ._potential_lammps import (potential_LAMMPS, potential_LAMMPS_df,
                                    load_potential_LAMMPS, _no_load_potential_LAMMPS,
                                    get_potential_LAMMPS, copy_potential_LAMMPS,
                                    download_LAMMPS_files)
    from ._widgets import (widget_search_potentials, widget_lammps_potential)

    def __init__(self, host=None, username=None, password=None, certification=None,
                 localpath=None, verbose=True, local=True, remote=True, 
                 load_citations=False, load_potentials=False,
                 load_potential_LAMMPS=False):
        """
        Class initializer

        Parameters
        ----------
        host : str, optional
            Remote host site to access.  Default value is
            'https://potentials.nist.gov/'
        username : str, optional 
            User name to use to access the host site.  Default value of '' will
            access the site as an anonymous visitor.
        password : str, optional
            Password associated with the given username.  Not needed for
            anonymous access.
        certification : str, optional
            File path to certification file if needed for host.
        localpath : str, optional
            Path to a local directory.  This can be used to hold user-defined
            records and/or a local copy of the database's records.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.
        local : bool, optional
            Indicates if the load operations will check localpath for records.
            Default value is True.
        remote : bool, optional
            Indicates if the load operations will download records from the
            remote database.  Default value is True.  If a local copy exists,
            then setting this to False is considerably faster.
        load_citations : bool, optional
            If True, the citations will be loaded during initialization.
            Default value is False.
        load_potentials : bool, optional
            If True, the potentials will be loaded during initialization.
            Default value is False.
        load_potential_LAMMPS : bool, optional
            If True, the LAMMPS potentials will be loaded during initialization.
            Default value is False.
        """
        # Set default database parameters
        if host is None:
            host = 'https://potentials.nist.gov/'
        if username is None:
            username = ''
        
        # Create the underlying CDCS client
        self.__cdcs = CDCS(host=host, username=username, password=password,
                           certification=certification)
        
        # Define class attributes
        self.__localpath = localpath
        assert isinstance(local, bool)
        assert isinstance(remote, bool)
        self.__local = local
        self.__remote = remote

        # Load records
        if load_citations:
            self.load_citations(verbose=verbose)
        else:
            self._no_load_citations()
        if load_potentials:
            self.load_potentials(verbose=verbose)
        else:
            self._no_load_potentials()
        if load_potential_LAMMPS:
            self.load_potential_LAMMPS(verbose=verbose)
        else:
            self._no_load_potential_LAMMPS()
    
    @property
    def cdcs(self):
        """cdcs.CDCS: REST client for database access"""
        return self.__cdcs
    
    @property
    def localpath(self):
        """str or None: path to the local copy of the database"""
        return self.__localpath

    @property
    def local(self):
        """bool : Indicates if load operations will check localpath"""
        return self.__local

    @property
    def remote(self):
        """bool : Indicates if load operations will check remote database"""
        return self.__remote

    def load_all(self, localpath=None, local=None, remote=None, verbose=False):
        """
        Loads records of all styles from the database, first checking localpath,
        then trying to download from host.

        Parameters
        ----------
        localpath : str, optional
            Path to a local directory to check for records first.  If not given,
            will check localpath value set during object initialization.  If not
            given or set during initialization, then only the remote database will
            be loaded.
        local : bool, optional
            Indicates if records in localpath are to be loaded.  If not given,
            will use the local value set during initialization.
        remote : bool, optional
            Indicates if the records in the remote database are to be loaded.
            Setting this to be False is useful/faster if a local copy of the
            database exists.  If not given, will use the local value set during
            initialization.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.
        """
        self.load_citations(localpath=localpath, local=local, remote=remote, verbose=verbose)
        self.load_potentials(localpath=localpath, local=local, remote=remote, verbose=verbose)
        self.load_potential_LAMMPS(localpath=localpath, local=local, remote=remote, verbose=verbose)

    def copy_all(self, localpath=None, format='xml', citeformat='bib', verbose=False):
        """
        Copies all loaded records to localhost.

        Parameters
        ----------
        localpath : str, optional
            Path to a local directory where the records are to be copied to.
            If not given, will check localpath value set during object
            initialization.
        format : str, optional
            The file format to save the results locally as.  Allowed values are
            'xml' and 'json'.  Default value is 'xml'.
        citeformat : str, optional
            The file format to save Citation records locally as.  Allowed
            values are 'xml', 'json', and 'bib'.  Default value is 'bib'.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.
        
        Raises
        ------
        ValueError
            If no localpath, no potentials, invalid format, or records in a
            different format already exist in localpath.
        """
        self.copy_citations(localpath=localpath, format=citeformat, verbose=verbose)
        self.copy_potentials(localpath=localpath, format=format, verbose=verbose)
        self.copy_potential_LAMMPS(localpath=localpath, format=format, verbose=verbose)