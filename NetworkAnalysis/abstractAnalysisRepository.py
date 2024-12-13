# -*- coding: utf-8 -*-

from qgis.core import (
    QgsProject,
    QgsGraduatedSymbolRenderer,
    QgsRendererRangeLabelFormat,
    QgsSymbol,
    QgsSimpleLineSymbolLayer,
    QgsSymbolLayer,
)
from qgis.core import (
    QgsStyle,
    QgsClassificationQuantile,
    QgsGradientColorRamp,
    QgsVectorLayer,
    QgsLayerTreeLayer,
    QgsVectorLayerJoinInfo,
)
from PyQt5.QtCore import QVariant
import requests
import os
from ..watering_utils import WateringUtils
from ..repositoriesLocalSHP.getDataRepository import getDataRepository


class AbstractAnalysisRepository:

    def __init__(self, token, analysisExecutionId, datetime, behavior):
        """Constructor."""
        self.token = token
        self.behavior = behavior
        self.analysisExecutionId = analysisExecutionId
        self.datetime = datetime

    def getResponse(self):
        params = {
            "analysisExecutionId": "{}".format(self.analysisExecutionId),
            "datetime": "{}".format(self.datetime),
            "behavior": "{}".format(self.behavior),
        }
        url = WateringUtils.getServerUrl() + self.UrlGet
        return requests.get(url, params=params, headers={"Authorization": "Bearer {}".format(self.token)})

    def elementAnalysisResults(self):
        print("Entering elementAnalysisResults")
        response = self.getResponse()
        filename = self.analysisExecutionId

        element_dict = {}
        for element in response.json()["data"]:
            element_dict[element[self.KeysApi[0]]] = [
                element[self.KeysApi[1]],
                element[self.KeysApi[2]],
                element[self.KeysApi[3]],
                element[self.KeysApi[4]],
            ]

            getDataRepository.analysis_to_csv(element, element, filename, self.datetime)
        """       
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
        self.changeColor() """

    def addCSVNonSpatialLayerToPanel(self, fileName, layerName):
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if not shapeGroup:
            shapeGroup = root.addGroup("Analysis")

        date = self.datetime.replace(":", "")
        project_path, scenario_id = (
            QgsProject.instance().readEntry("watering", "project_path", "default text")[0],
            QgsProject.instance().readEntry("watering", "scenario_id", "default text")[0],
        )
        print("Project path (addCSVNonSpatialLayerToPanel): ", project_path)
        print("Scenario ID: ", scenario_id)
        date_folder_path = os.path.join(project_path, scenario_id, "Analysis", date)

        self.loadCsvLayer(os.path.join(date_folder_path, fileName), layerName, shapeGroup)

    def loadCsvLayer(self, filepath, layer_name, group):
        uri = f"file:///{filepath}?type=csv&delimiter=,&detectTypes=yes&geomType=none"
        layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
        QgsProject.instance().addMapLayer(layer, False)
        if layer.isValid():
            group.addChildNode(QgsLayerTreeLayer(layer))
        else:
            print(f"{layer_name} failed to load! Error: {layer.error().message()}")

    def joinLayersAttributes(self, layerName, layerDest, join_field, fields_to_add):
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == layerName:
                source_layer = layer
            if layer.name() == layerDest:
                target_layer = layer
        if not source_layer or not target_layer:
            raise ValueError("One or both layers not found in the project!")

        joinObject = QgsVectorLayerJoinInfo()
        joinObject.setJoinFieldName(join_field)
        joinObject.setTargetFieldName("ID")
        joinObject.setJoinLayerId(source_layer.id())
        joinObject.setUsingMemoryCache(True)
        joinObject.setJoinLayer(source_layer)
        joinObject.setJoinFieldNamesSubset(fields_to_add)
        # joinObject.setPrefix(self.analysisExecutionId)
        target_layer.addJoin(joinObject)
        self.changeColor(self.Field)

    def changeColor(self, fieldName):
        # Set layer name and desired paremeters
        num_classes = 7
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
        renderer.setClassAttribute(fieldName)
        renderer.setClassificationMethod(classification_method)
        renderer.setLabelFormat(format)
        renderer.updateClasses(layer, num_classes)
        renderer.updateColorRamp(color_ramp)
        renderer.setSymbolSizes(self.Size, self.Size)

        layer.setRenderer(renderer)
        layer.triggerRepaint()
