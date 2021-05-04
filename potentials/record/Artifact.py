# coding: utf-8
# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from datamodelbase.record import Record

class Artifact(Record):
    """
    Class for describing artifacts (files accessible online)
    """
    def __init__(self, model=None, filename=None, label=None, url=None):
        """
        Initializes an Artifact object to describe a file accessible online

        Parameters
        ----------
        model : str or DataModelDict, optional
            Model content or file path to model content.
        filename : str, optional
            The name of the file without path information.
        label : str, optional
            A short description label.
        url : str, optional
            URL for file where downloaded, if available.
        """
        if model is not None:
            try:
                assert filename is None
                assert label is None
                assert url is None
            except:
                raise TypeError('model cannot be given with any other parameter')
            else:
                self.load_model(model)
        else:
            self.set_values(filename=filename, label=label, url=url)

    @property
    def modelroot(self):
        return 'artifact'

    @property
    def xsl_filename(self):
        return ('potentials.xsl', 'artifact.xsl')

    @property
    def xsd_filename(self):
        return ('potentials.xsd', 'artifact.xsd')

    @property
    def filename(self):
        """str or None: name of the file"""
        return self.__filename
    
    @filename.setter
    def filename(self, v):
        if v is None:
            self.__filename = None
        else:
            self.__filename = str(v)

    @property
    def label(self):
        """str or None: short descriptive label"""
        return self.__label
    
    @label.setter
    def label(self, v):
        if v is None:
            self.__label = None
        else:
            self.__label = str(v)
    
    @property
    def url(self):
        """str or None: URL where file can be downloaded"""
        return self.__url
    
    @url.setter
    def url(self, v):
        if v is None:
            self.__url = None
        else:
            self.__url = str(v)

    def set_values(self, filename=None, label=None, url=None):
        """
        Sets an Artifact object's attributes

        Parameters
        ----------
        filename : str, optional
            The name of the file without path information.
        label : str, optional
            A short description label.
        url : str, optional
            URL for file where downloaded, if available.
        """
        self.filename = filename
        self.label = label
        self.url = url

    def load_model(self, model):
        """"
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        """
        artifact = DM(model).find('artifact')
        self.url = artifact['web-link'].get('URL', None)
        self.label = artifact['web-link'].get('label', None)
        self.filename = artifact['web-link'].get('link-text', None)
    
    def build_model(self):
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict
            The data model content.
        """

        model = DM()
        model['artifact'] = DM()
        model['artifact']['web-link'] = DM()
        if self.url is not None:
            model['artifact']['web-link']['URL'] = self.url
        if self.label is not None:
            model['artifact']['web-link']['label'] = self.label
        if self.filename is not None:
            model['artifact']['web-link']['link-text'] = self.filename
        
        return model

    def metadata(self):
        """Returns a flat dict representation of the object"""
        meta = {}
        meta['filename'] = self.filename
        meta['label'] = self.label
        meta['url'] = self.url

        return meta