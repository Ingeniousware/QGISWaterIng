# -*- coding: utf-8 -*-

"""
***************************************************************************
    INPManager.py
    ---------------------
    Date                 : Nomviembre 2024
    Copyright            : (C) 2024 by Ingeniowarest
    Email                : 
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Ingenioware                                                       *
*                                                                         *
***************************************************************************
"""

import csv
import os
from qgis.core import (QgsProject, QgsVectorLayer, QgsLayerTreeLayer, QgsVectorLayerJoinInfo, QgsClassificationQuantile,
                       QgsRendererRangeLabelFormat, QgsStyle, QgsGradientColorRamp, QgsGraduatedSymbolRenderer)

from ..watering_utils import WateringUtils



class AbstractAnalysis:
    """
    Clase base para la visualización de lo los resultado de la modelación en QGIS.
    """

    def __init__(self, analysisExecutionId, datetime):
        """Constructor for Abstract Analysis"""
        self.analysisExecutionId = analysisExecutionId
        self.datetime = datetime
    
    
    def __loadCsvLayer(self, filepath, layer_name, group):
        """
        Carga el layer en el grupo especificado para ser visualizado.
        """
        uri = f"file:///{filepath}?type=csv&delimiter=,&detectTypes=yes&geomType=none"
        layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
        QgsProject.instance().addMapLayer(layer, False)
        if layer.isValid():
            group.addChildNode(QgsLayerTreeLayer(layer))
        else:
            print(f"{layer_name} failed to load! Error: {layer.error().message()}")
    
    
    def addCSVNonSpatialLayerToPanel(self, fileName, layerName):
        """
        Agrega un layer no espacial a la ventana de resultados a partir de un fichero CSV.
        """
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

        self.__loadCsvLayer(os.path.join(date_folder_path, fileName), layerName, shapeGroup)
    
    
    def __changeColor(self, fieldName):
        """
        Especifica la escala de color de layer que se va a representar.
        """
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
    
    
    def joinLayersAttributes(self, layerName, layerDest, join_field, fields_to_add):
        """
        """
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
        self.__changeColor(self.Field)
    
    
    def analysis_to_csv(self, element, filename, date):
        """
        """
        def write_to_csv(filepath, keys):

            file_exists = os.path.isfile(filepath)
            with open(filepath, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(keys)
                writer.writerow([element[key] for key in keys])

        date = date.replace(":", "")
        project_path = WateringUtils.getProjectPath()
        scenario_id = QgsProject.instance().readEntry("watering", "scenario_id", "default text")[0]
        scenario_folder_path = project_path + "/" + scenario_id
        analysis_folder_path = scenario_folder_path + "/" + "Analysis"
        date_folder_path = analysis_folder_path + "/" + date

        # Create analysis folder
        os.makedirs(analysis_folder_path, exist_ok=True)
        # Create date folder inside analysis
        os.makedirs(date_folder_path, exist_ok=True)

        pipe_keys = [
            "serverKeyId",
            "pipeKey",
            "simulationDateTime",
            "pipeCurrentStatus",
            "velocity",
            "flow",
            "headLoss",
        ]
        node_keys = ["serverKeyId", "nodeKey", "simulationDateTime", "pressure", "waterDemand", "waterAge"]
        # File for pipes analysis
        if all(key in element for key in pipe_keys):
            pipes_filepath = os.path.join(date_folder_path, f"{filename}_Pipes.csv")
            write_to_csv(pipes_filepath, pipe_keys)
        # File for nodes analysis
        if all(key in element for key in node_keys):
            nodes_filepath = os.path.join(date_folder_path, f"{filename}_Nodes.csv")
            write_to_csv(nodes_filepath, node_keys)