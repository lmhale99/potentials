# coding: utf-8
from pathlib import Path

from cdcs import CDCS

from .. import Settings
from ..tools import aslist

class Database():
    """
    Class for interacting with potential records hosted from potentials.nist.gov
    """
    # Class imports
    from ._record import (get_records, get_record, download_records,
                          upload_record, delete_record)

    from ._citation import (citations, citations_df, 
                            load_citations, _no_load_citations,
                            get_citations, get_citation,
                            download_citations, upload_citation,
                            save_citations, delete_citation)

    from ._potential import (potentials, potentials_df,
                             load_potentials, _no_load_potentials,
                             get_potentials, get_potential,
                             download_potentials, upload_potential,
                             save_potentials, delete_potential)

    from ._kim_potential import (installed_kim_models, init_installed_kim_models,
                                 default_kim_settings_file, load_kim_lammps_potentials,
                                 find_installed_kim_models, set_installed_kim_models,
                                 save_installed_kim_models, load_installed_kim_models)

    from ._lammps_potential import (lammps_potentials, lammps_potentials_df,
                                    load_lammps_potentials, _no_load_lammps_potentials,
                                    get_lammps_potentials, get_lammps_potential,
                                    download_lammps_potentials, upload_lammps_potential,
                                    get_lammps_potential_files, save_lammps_potentials,
                                    delete_lammps_potential)

    from ._widgets import (widget_search_potentials, widget_lammps_potential)

    def __init__(self, host=None, username=None, password=None, certification=None,
                 localpath=None, verbose=False, local=None, remote=None, 
                 load=False, status='active', installed_kim_models=None,
                 kim_api_directory=None, kim_settings_file=None):
        """
        Class initializer

        Parameters
        ----------
        host : str, optional
            CDCS site to access.  Default value is 'https://potentials.nist.gov/'.
        username : str, optional 
            User name to use to access the host site.  Default value of '' will
            access the site as an anonymous visitor.
        password : str, optional
            Password associated with the given username.  Not needed for
            anonymous access.
        certification : str, optional
            File path to certification file if needed for host.
        localpath : str, optional
            Path to the local library directory to use.  If not given, will use
            the set library_directory setting.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.
        local : bool, optional
            Indicates if the load operations will check localpath for records.
            Default value is controlled by settings.
        remote : bool, optional
            Indicates if the load operations will download records from the
            remote database.  Default value is controlled by settings.  If a
            local copy exists, then setting this to False is considerably
            faster.
        load : bool, str or list, optional
            If True, citations, potentials and lammps_potentials will all be
            loaded during initialization. If False (default), none will be
            loaded.  Alternatively, a str or list can be given to specify which
            of the three record types to load.
        status : str, list or None, optional
            Only potential_LAMMPS records with the given status(es) will be
            loaded.  Allowed values are 'active' (default), 'superseded', and
            'retracted'.  If None is given, then all potentials will be loaded.
        installed_kim_models : str or list, optional
            Allows for the list of installed_kim_models to be explicitly given.
            Cannot be given with the other parameters.
        kim_api_directory : path-like object, optional
            The directory containing the kim api to use to build the list.
        kim_settings_file : path-like object, optional
            The path to a json file with an 'installed-kim-models' field that lists
            the installed kim models.
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
        if localpath is None:
            self.__localpath = Settings().library_directory
        else:
            self.__localpath = Path(localpath)
        
        # Handle local/remote settings
        if local is None:
            local = Settings().local
        if remote is None:
            remote = Settings().remote
        assert isinstance(local, bool)
        assert isinstance(remote, bool)
        self.__local = local
        self.__remote = remote

        # Initialize kim settings
        self.init_installed_kim_models(installed_kim_models=installed_kim_models,
                                       kim_api_directory=kim_api_directory,
                                       kim_settings_file=kim_settings_file)

        # Load records
        if load is True:
            self.load_all(verbose=verbose)
        elif load is False:
            self._no_load_citations()
            self._no_load_potentials()
            self._no_load_lammps_potentials()
        else:
            load = aslist(load)
        
            if 'citations' in load:
                self.load_citations(verbose=verbose)
                load.remove('citations')
            else:
                self._no_load_citations()
            if 'potentials' in load:
                self.load_potentials(verbose=verbose)
                load.remove('potentials')
            else:
                self._no_load_potentials()
            if 'lammps_potentials' in load:
                self.load_lammps_potentials(verbose=verbose, status=status)
                load.remove('lammps_potentials')
            else:
                self._no_load_lammps_potentials()

            if len(load) > 0:
                raise ValueError('unknown load type: allowed values are citations, potentials, and lammps_potentials')

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

    def load_all(self, localpath=None, local=None, remote=None, status='active',
                 verbose=False):
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
        status : str, list or None, optional
            Only potential_LAMMPS records with the given status(es) will be
            loaded.  Allowed values are 'active' (default), 'superseded', and
            'retracted'.  If None is given, then all potentials will be loaded.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.
        """
        self.load_citations(localpath=localpath, local=local, remote=remote,
                            verbose=verbose)
        self.load_potentials(localpath=localpath, local=local, remote=remote,
                             verbose=verbose)
        self.load_lammps_potentials(localpath=localpath, local=local,
                                    remote=remote, status=status,
                                    verbose=verbose)

    def download_all(self, localpath=None, format='xml', citeformat='bib',
                     indent=None, status='active', verbose=False,
                     downloadfiles=True):
        """
        Downloads all records from the remote to localhost.

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
        indent : int, optional
            The indentation spacing size to use for the locally saved record files.
            If not given, the JSON/XML content will be compact.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.
        status : str, list or None, optional
            Only potential_LAMMPS records with the given status(es) will be
            downloaded.  Allowed values are 'active' (default), 'superseded', and
            'retracted'.  If None is given, then all potentials will be downloaded.
        downloadfiles : bool, optional
            If True, the parameter files associated with the potential_LAMMPS
            record will also be downloaded.
        
        Raises
        ------
        ValueError
            If no localpath, no potentials, invalid format, or records in a
            different format already exist in localpath.
        """
        self.download_citations(localpath=localpath, format=citeformat,
                                indent=indent, verbose=verbose)

        self.download_potentials(localpath=localpath, format=format,
                                 indent=indent, verbose=verbose)

        self.download_lammps_potentials(localpath=localpath, format=format,
                                        indent=indent, verbose=verbose,
                                        status=status, downloadfiles=downloadfiles)