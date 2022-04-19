# coding: utf-8
# Standard Python libraries
from typing import Optional

# https://github.com/usnistgov/yabadaba
import yabadaba

# Local imports
from .. import settings

def load_database(name: Optional[str] = None,
                  style: Optional[str] = None,
                  host: Optional[str] = None,
                  **kwargs) -> yabadaba.database.Database:
    """
    Loads a database object.  Can be either loaded from stored settings or
    by defining all needed access information.
    
    Parameters
    ----------
    name : str, optional
        The name assigned to a pre-defined database.  If given, can be the only
        parameter.
    style : str, optional
        The database style to use.
    host : str, optional
        The URL/file path where the database is hosted.
    kwargs : dict, optional
        Any other keyword parameters defining necessary access information.
        Allowed keywords are database style-specific.
    
    Returns
    -------
    Subclass of yabadaba.Database
        The database object.
    """
    return yabadaba.load_database(name=name, style=style, host=host,
                                  settings=settings, **kwargs)
