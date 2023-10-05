import os
import requests

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsLayerTreeLayer
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsSymbol, edit
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import pandas as pd
import numpy as np
from datetime import date, timedelta
import time


class getDataRepository:
    def __init__(self,token, projectFK):
        """Constructor."""
        super(getDataRepository, self).__init__(token, projectFK)      
        self.token = token
        self.ProjectFK = projectFK

    def get_date_range(self):
                                     
        # See the data from the last x days
        dateSelected = self.selectdate_box.currentIndex()

        if dateSelected == 0:
            finalDate = date.today()
            initialDate = finalDate - timedelta(days=30)
            
        elif dateSelected == 1:
            finalDate = date.today()
            initialDate = finalDate - timedelta(days=15)
        
        else:
            initialDate = self.inicial_dateEdit.date().toPyDate() 
            finalDate = self.final_dateEdit.date().toPyDate()
        
        initialDate = f"{initialDate} 00:00:00"
        finalDate =  f"{finalDate} 00:00:00"
        
        return(initialDate, finalDate)

    def createDataFrame_api(self):
        
        url_Measurements = "https://dev.watering.online/api/v1/measurements"
        channelFK =  self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][0]
        
        initialDate, finalDate = (getDataRepository.get_date_range(self))
        params = {'channelKeyId': "{}".format(channelFK), 'startDate': "{}".format(initialDate),'endDate': "{}".format(finalDate)}

        headers={'Authorization': "Bearer {}".format(self.token)}
        selectColumns = ['value', 'timeStamp']

        response_analysis = requests.get(url_Measurements, params=params, headers=headers)
        response_analysis.raise_for_status()
        data = response_analysis.json()["data"]

        if data == []:
            return pd.DataFrame(data) 

        df = pd.DataFrame(data)[selectColumns]
        
        return(df)