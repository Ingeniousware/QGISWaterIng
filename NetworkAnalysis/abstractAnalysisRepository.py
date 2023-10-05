# -*- coding: utf-8 -*-

from qgis.core import QgsProject, QgsGraduatedSymbolRenderer, QgsRendererRangeLabelFormat
from qgis.core import QgsStyle, QgsClassificationQuantile, QgsGradientColorRamp

import requests
from ..watering_utils import WateringUtils

class AbstractAnalysisRepository():
    
    def __init__(self,token,analysisExecutionId,datetime,behavior):
        """Constructor."""
        self.token = token
        self.behavior = behavior
        self.analysisExecutionId = analysisExecutionId
        self.datetime = datetime
        
    def getResponse(self):
        params = {'analysisExecutionId': "{}".format(self.analysisExecutionId), 'datetime': "{}".format(self.datetime),
                          'behavior': "{}".format(self.behavior)}
        url = WateringUtils.getServerUrl() + self.UrlGet
        return requests.get(url, params=params, headers={'Authorization': "Bearer {}".format(self.token)})
    
    def elementAnalysisResults(self):     
        response = self.getResponse()
        
        element_dict = {}
        for element in response.json()["data"]:
            element_dict[element[self.KeysApi[0]]] = [element[self.KeysApi[1]], element[self.KeysApi[2]], 
                                 element[self.KeysApi[3]], element[self.KeysApi[4]]]
            
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]

        layer.startEditing()
        idx_att1 = layer.fields().indexOf(self.Attributes[0])
        idx_att2 = layer.fields().indexOf(self.Attributes[1])
        idx_att3 = layer.fields().indexOf(self.Attributes[2])
        idx_att4 = layer.fields().indexOf(self.Attributes[3])
        
        for feature in layer.getFeatures():
            if feature['ID'] in element_dict:
                element = element_dict[feature['ID']]
                layer.changeAttributeValue(feature.id(), idx_att1, element[0])
                layer.changeAttributeValue(feature.id(), idx_att2, element[1])
                layer.changeAttributeValue(feature.id(), idx_att3, element[2])
                layer.changeAttributeValue(feature.id(), idx_att4, element[3])
                
        layer.commitChanges()
        
        print(self.LayerName, "analysis results done, behavior: ", self.behavior)
        
        self.changeColor()
    
    def changeColor(self):
        # Set layer name and desired paremeters
        num_classes = 10
        classification_method = QgsClassificationQuantile()
        
        layer = QgsProject().instance().mapLayersByName(self.LayerName)[0]
        
        # change format settings as necessary
        format = QgsRendererRangeLabelFormat()
        format.setFormat("%1 - %2")
        format.setPrecision(2)
        format.setTrimTrailingZeroes(True)
        
        # Create the color ramp
        default_style = QgsStyle().defaultStyle()
        color_ramp = QgsGradientColorRamp(self.StartColor, self.EndColor)
        renderer = QgsGraduatedSymbolRenderer()
        renderer.setClassAttribute(self.Field)
        renderer.setClassificationMethod(classification_method)
        renderer.setLabelFormat(format)
        renderer.updateClasses(layer, num_classes)
        renderer.updateColorRamp(color_ramp)
        renderer.setSymbolSizes(self.Size, self.Size)
        layer.setRenderer(renderer)
        layer.triggerRepaint()