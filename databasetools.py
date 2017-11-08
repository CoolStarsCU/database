from astrodbkit import astrodb
from astropy.io import fits
from contextlib import redirect_stdout
import pandas as pd
import numpy as np
import re
import io
import os
import math
import csv
import pip
 
Dependencies = [
    'astrodbkit',
    'numpy',
    'pandas']


class dbtools:
    """
    Columbia University Astronomy Lab database handler
    """
    def __init__(self):
        
        """This is the __init_ section of the class where initial constants, variables etc are declared and other
        initial namespace operations are performed"""
        
        
        #Schema of the Database
        
        self.database_schema = {
            
        #Keys are table names and values are column names within the tables  

            'SOURCES': ['id','ra','dec','designation','publication_shortname','names','components',
                        'companions','comments','version'],
            
            'CHANGELOG': ['id','date','user','machine_name','modified_tables','user_description','filename'],
            
            'IGNORE': ['id','id1','id2','tablename'],
            
            'MODES':['id','mode','publication_shortname'],
            
            'SYSTEMS': ['id','name','publication_shortname'],
            
            'PUBLICATIONS':['id','bibcode','shortname','DOI','description'],
            
            'INSTRUMENTS' : ['id', 'name', 'publication_shortname'],
            
            'TELESCOPES' : ['id','name','publication_shortname'],
            
            'DATA_REQUESTS' : ['id','source_id','source','data_request','purpose'],
            
            'VERSIONS' : ['id', 'version', 'data_published', 'publication_shortname', 'comment'],
            
            'PHOTOMETRY': ['id','source_id','band','magnitude','magnitude_unc','system_id','telescope_id',
                            'instrument_id', 'publication_shortname','epoch','comments','versions'],
            
            'SPECTRAL_TYPES' : ['id','source_id','spectral_type','spectral_type_unc','publication_shortname','adopted',
                                'comments','version','num_spt','num_spt_unc'],
            
            'PARALLAXES' : ['id','source_id','parallax','parallax_unc','publication_shortname','adopted','comments',
                            'version'],
            
            'PROPER_MOTIONS' : ['id', 'source_id', 'proper_motion_ra','proper_motion_ra_unc', 'proper_motion_dec',
                                'proper_motion_dec_unc','V_tan','V_tan_unc','publication_shortname',
                                'comments', 'versions'],
            
            'RADIAL_VELOCITIES' : ['id','source_id','radial_velocity','radial_velocity_unc','spectrum_id',
                                   'publication_shortname','comments','version'],
            
            'SPECTRA' : ['id', 'source_id', 'spectrum' ,'wavelength_units', 'flux_units' ,'wavelength_order',
                         'regime','publication_shortname','obs_date','instrument_id','telescope_id','mode_id',
                         'filename','comments','best','version','local_spectrum'],
            
            'COMPANIONS' : ['id','source_id','publication_shortname','type','n', 'status'],
            
            'ACTIVITY' : ['id','source_id','regime','line','wavelength_min','wavelength_max', 'frequency_min', 
                          'frequency_max','ew','ew_unc','l_lbol','l_lbol_unc','flux','flux_unc','publication_shortname',
                          'epoch','telescope_id','instrument_id','spectrum_id','comments'],
            
            'MEMBERSHIP' : ['id', 'source_id', 'publication_shortname', 'pmem', 'pmem_unc' ,'comments'],
            
            'MODELS' : ['id', 'model', 'publication_shortname'],
            
            'MASS' : ['id', 'source_id', 'mass', 'mass_unc', 'model_id', 'publication_shortname', 'comments'],
            
            'ROTATION' : ['id', 'source_id', 'publication_shortname', 'period', 'period_unc','telescope_id',
                          'instrument_id','comments','tau','tau_model_id','adopted']
            
        }
        
        
        #Dictonary where primary_ids are stored
        
        self.primary_id_dict = {
            
            'SOURCES': 0,
            'CHANGELOG': 0,
            'IGNORE' : 0,
            'MODES' : 0,
            'SYSTEMS' : 0,
            'PUBLICATIONS': 0,
            'INSTRUMENTS' : 0,
            'TELESCOPES': 0,
            'DATA_REQUESTS' : 0,
            'VERSIONS': 0,
            'PHOTOMETRY': 0,
            'SPECTRAL_TYPES' : 0,
            'PARALLAXES' : 0,
            'PROPER_MOTIONS' : 0,
            'RADIAL_VELOCITIES' : 0,
            'SPECTRA' : 0,
            'COMPANIONS': 0,
            'ACTIVITY' : 0,
            'MEMBERSHIP' : 0,
            'MODELS' : 0,
            'MASS' : 0,
            'ROTATION' : 0
            
        }
        
        
        for key in self.primary_id_dict:
            
            self.primary_id_dict[key] = self.get_index('tabledata/{}.sql'.format(key))
            
            
        self.source_id = 0
        
        #none value array            
        self.globalnulls = [-9999.0,-99.0,'no string','X','None','Nan','nan']
        
    # def remove none values using none value dict
    #def check mapping file is ok (check for ' )
    
    # add the latest row check for .sql creation
    
    # take backups
    
    #HELPER FUNCTIONS
    
    #creates an empty mapping file to be used when auto importing a fits file
    def create_mapping(self, filename = 'mapping.csv'):
        """Creates an unfilled csv file with column names of the database and empty rows that can be
        filled in order to map the .fits file into the csv. 
        """

        with open(filename, 'w') as csvfile:

            writer = csv.writer(csvfile)


            for key in self.database_schema:
                writer.writerow([key] + self.database_schema[key])


                for i in range(5):

                    writer.writerow('\n')
        
        print('Completed')
        
        
    #gets the highest index number from .sql data files
    def get_index(self,filename):
    
        try:
            for line in reversed(open(filename).readlines()):
                

                if '\n' == line:
                    continue
                    
                index = int(re.search('[0-9]+',line)[0])
                
                break
                
            return index

        except FileNotFoundError:
            return 0
        

    def write_row(self,tablename,valuesarray):
        
        """Writes a row of data values given in valuesarray into the given tablename
        
        Parameters
        ----------
        tablename: str
            name of the table in which the data will be inserted
                
        valuesarray: python array
            array of values to be inserted into the database
                
        Comments
        --------
        This function can be used to override the astrodbkit wrapper whenever it doesn't work.
        
        """
        self.primary_id_dict[tablename] += 1

        values = [str(i) for i in valuesarray]

        values[0] = str(self.primary_id_dict[tablename])
        
        
        if tablename != 'SOURCES':
            values[1] = str(self.source_id)

        if not os.path.exists('tabledata'):
            os.makedirs('tabledata')

            
        file = open('tabledata/{}.sql'.format(tablename.lower()),'a+')

        file.write("INSERT INTO '{}' VALUES\n".format(tablename))

        valuestowrite = '({});\n'.format(','.join(values))
        
        file.write(valuestowrite)

        file.close()

        
        

    #END HELPER FUNCTIONS
            
            
        """    def add_statics():
        """
        
        
    def add_statics(self):
        
        
        self.publications=[
                'dotter2008','delfosse2000','kraus2007','douglas2014','agueros2011','kovacs2014','kafka2006',
                'skrutskie2006','zacharias2012']
        
        self.telescopes = [ 
                'SDSS','2MASS','WISE','UKIRT','HST','Spitzer','IRTF','Keck I','Keck II','KPNO 4m',
                'KPNO 2.1m','KPNO Bok','MMT','CTIO 1.5m','CTIO 4m','Gemini North','Gemini South',
                'ARC 3.5m','Subaru','Magellan I Baade','Magellan II Clay','ESO 1m','CFHT','NTT',
                'Palomar 200-inch','Pan-STARRS 1','Palomar 60-inch','CTIO 0.9m','SOAR 4.1m','GTC',#30
                'ESO VLT U1','ESO VLT U2','ESO VLT U3','ESO VLT U4','MDM 2.4m','MDM 1.3m','WIYN 3.5m'
                'Mayall']
        
        self.instruments = [
                'R-C Spec','GMOS-N','GMOS-S','FORS','LRIS','SpeX','LDSS3','FOCAS','NIRSPEC','IRS',#10
                'FIRE','MagE','GoldCam','SINFONI','OSIRIS','Triplespec','X-Shooter','GNIRS','WIRCam','CorMASS',#20
                'ISAAC','IRAC','DIS','SuSI2','IRCS','NIRI','P1640','NIFS','STIS','CGS4'#30
                'NIRC','IRCAM','SPHERE','WFC3','SofI','WIRCam','NICI','PANIC','NEWFIRM','UIST',#40
                'MegaCam','UFTI','MIKE','GPI','NaCo','FourStar','Flamingos2','ModSpec','Hydra','SDSS-I/II',#50
                'APOGEE','BOSS','OSMOS']
        
        self.modes = [
                'Prism','SXD','LXD1.9','SL','LXD2.3', 'Echelle','LL','VPH Grism','Red Grism']
        
        self.systems = [
                'SDSS','2MASS','WISE','AB','ST','Vega','MKO','CIT','Johnson','Cousins',#10
                'Landolt','Stromgren','Bessel','GALEX','DENIS','APASS','Kepler','Gaia']
        
        self.models = [
                'dotter','dotter2008','delfosse2000','kraus2007']
        
        
        #CHECK FOR NEW MODEL NAMES?,
        
    def add_fits(self, fitsfile, csvmapfile):
        
        """ automatically populates the database from the fits file using the mapping.csv 
        file that links the two
        
        Parameters
        ----------
            fits_file: str 
                The name and path of the Flexible Image Transport System file
                
            cvsmapfile: str
                the name and path of the .csv file with a particular expected format that is used to map the 
                values in the fits file to database
        
        Constructs
        ----------
            .sql files that can be used by astrodbkit to add data into the database

        """
        
        
        # open the fits file and save the data segment into a variable
        fitsdata = fits.open(fitsfile)[1].data

        # open the .csv file for mapping and save into a variable
        mapping = pd.read_csv(csvmapfile,header=None,na_values='\n')
        
        #get the headers of the fits file
        fitscolumnnames = fitsdata.columns.names
        


        
        for datarow in fitsdata:
            
            
            #increment source_id which is unique for each .fits row
            self.source_id += 1
            
            
            for index,row in mapping.iterrows():
                
                
                #gate that switches to the current tablename based on the mapping.csv file
                if type(row[0]) != float:
                    
                    tablename = row[0]
                    
                    schema = self.database_schema[tablename.upper()]
                    
                    #continue to next column as the first column is just for table names
                    continue 
                
                    
                #The .csv file returns a float(nan) object as None so float means we are at a row with values.
                elif type(row[0]) == float:

                    values = ['NULL'] * len(schema)
                    servicearray = []

                    for i in range(len(row)):
                        
                        
                        if type(row[i]) == float:

                            if math.isnan(row[i]):
                                continue

                            else:
                                values[i-1] = str(row[i])

                        else:

                            split = row[i].split(',')

                            if row[i] in fitscolumnnames:
                                
                                servicearray.append(datarow[row[i]])
                                
                                try:
                                    float(str(datarow[row[i]]))
                                    values[i-1] = datarow[row[i]]

                                except ValueError:
                                    values[i-1] = "'{}'".format(datarow[row[i]])

                                    
                            elif len(split) > 1 and split[0] in fitscolumnnames :
                                
                                package = [str(datarow[header]) for header in split]

                                values[i-1] = "'{}'".format(','.join(package))

                            else:
                                values[i-1] =  "'{}'".format(row[i])

                                
                nullvalues = [i for i in servicearray if i in self.globalnulls]
                
                
                if values.count('NULL') < len(values) and len(nullvalues) != len(servicearray):
                    
                    
                    if tablename == 'SOURCES':
                                               
                        sourcenulls = [-9999.0,-99.0,'no string','X',0,-9999,'-9999','-9999.0','-99.0','0']
                        
                        valuestosplit = re.sub("'","",values[5])
                        sourcenamevalue = valuestosplit.split(',')

                        sourcenames = [ 'ASAS','','2MASS','SWASP','USNO','UCAC','GOLDMAN','EPIC']

                        zippedsourcenames = list(zip(sourcenames,sourcenamevalue))
                
                        values[5] = "'{}'".format(','.join(['{} {}'.format(i,j) for (i,j)\
                                                           in zippedsourcenames if j not in sourcenulls]))
                        
                        self.write_row(tablename,values) 
                        
                        
                    else:
                        
                        self.write_row(tablename,values) 

                else:
                    continue

            
            
            
        
        
