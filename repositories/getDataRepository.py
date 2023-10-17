from qgis.core import QgsProject
import os
import requests
import pandas as pd
import numpy as np
from datetime import date, timedelta
import time
import csv

class getDataRepository:
    def __init__(self,token, projectFK):
        """Constructor."""
        super(getDataRepository, self).__init__(token, projectFK)      
        self.token = token
        self.ProjectFK = projectFK

    def get_date_range(self):
                                     
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

    def analysis_to_csv(self, element, filename, date):

        def write_to_csv(filepath, keys):
            
            file_exists = os.path.isfile(filepath)
            with open(filepath, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(keys)
                writer.writerow([element[key] for key in keys])

        project_path = QgsProject.instance().readEntry("watering","project_path","default text")[0]
        scenario_id = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        scenario_folder_path = project_path + "/" + scenario_id
        analysis_folder_path = scenario_folder_path + "/" + "Analysis"
        date_folder_path = analysis_folder_path + "/" + date
        
        #Create analysis folder
        os.makedirs(analysis_folder_path, exist_ok=True)
        #Create date folder inside analysis
        os.makedirs(date_folder_path, exist_ok=True)

        pipe_keys = ['serverKeyId', 'simulationDateTime', 'pipeCurrentStatus', 'velocity', 'flow', 'headLoss']
        node_keys = ['serverKeyId', 'simulationDateTime', 'pressure', 'waterDemand', 'waterAge']
        # File for pipes analysis
        if all(key in element for key in pipe_keys):
            pipes_filepath = os.path.join(date_folder_path, f"{filename}_Pipes.csv")
            write_to_csv(pipes_filepath, pipe_keys)
        # File for nodes analysis
        if all(key in element for key in node_keys):
            nodes_filepath = os.path.join(date_folder_path, f"{filename}_Nodes.csv")
            write_to_csv(nodes_filepath, node_keys)
