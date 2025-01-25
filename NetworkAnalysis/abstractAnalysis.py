# -*- coding: utf-8 -*-

"""
***************************************************************************
    abstractAnalysis.py
    ---------------------
    Date                 : Enero 2025
    Copyright            : (C) 2025 by Ingeniowarest
    Email                : 
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Ingenioware                                                       *
*                                                                         *
***************************************************************************
"""

from abc import ABC, abstractmethod
import csv
import os

from qgis.core import (QgsProject, QgsVectorLayer, QgsLayerTreeLayer, QgsVectorLayerJoinInfo, QgsClassificationQuantile,
                       QgsRendererRangeLabelFormat, QgsStyle, QgsGradientColorRamp, QgsGraduatedSymbolRenderer)

from ..INP_Manager.inp_utils import INP_Utils

class AbstractAnalysis(ABC):
    def __init__(self, analysisExecutionId, datetime):
        """Constructor for Abstract Analysis"""
        self.analysisExecutionId = analysisExecutionId
        self.datetime = datetime


    @abstractmethod
    def elementAnalysisResults(self):
         print("Método base no implementado...")


    def loadCSVLayer(self, filepath, layer_name, group):
        """
        Carga el layer en el grupo especificado para ser visualizado.
        
        Parameters
        ----------
        filepath: str
            Nombre del fichero.
        layer_name: str
            Nombre del layer no espacial.
        group: QgsLayerTreeGroup
            Grupo donde se agrupan los layers de análisis.
        """
        uri = f"file:///{filepath}?type=csv&delimiter=,&detectTypes=yes&geomType=none"
        layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
        QgsProject.instance().addMapLayer(layer, False)
        if layer.isValid():
            group.addChildNode(QgsLayerTreeLayer(layer))
        else:
            print(f"{layer_name} failed to load! Error: {layer.error().message()}")


    @abstractmethod
    def addCSVNonSpatialLayerToPanel(self, fileName, layerName):
        """
        Agrega un layer no espacial a la ventana de resultados a partir de un fichero CSV.
        
        Parameters
        ----------
        fileName: str
            Nombre del fichero.
        layerName: str
            Nombre del layer no espacial.
        """
        print("Método base no implementado...")
    
    
    def changeColor(self, fieldName):
        """
        Especifica la escala de color de layer que se va a representar.
        
        Parameters
        ----------
        fileName: str
            Nombre del fichero.
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
        Método a junata el layes con los attributes especificados.
        
        Parameters
        ----------
        layerName: str
            Nombre de la capa.
        layerDest: str
            Nombre del layer que se va a unir.
        join_field:
            Campo por el se va a efectuar la union.
        fields_to_add:
            Campos que se van a adicionar.
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
        self.changeColor(self.Field)