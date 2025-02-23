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
"""
# Importar las bibliotecas necesarias
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsDataSourceUri,
    QgsField,
    QgsFeature,
)
from qgis.PyQt.QtCore import QVariant

# Ruta al archivo CSV
csv_file = 'ruta/a/tu/archivo.csv'

# Cargar el archivo CSV como una capa
csv_layer = QgsVectorLayer(csv_file + "?delimiter=,", "CSV Layer", "delimitedtext")
if not csv_layer.isValid():
    print("Error al cargar el archivo CSV.")
else:
    QgsProject.instance().addMapLayer(csv_layer)

# Cargar la capa geoespacial (por ejemplo, un shapefile)
shapefile = 'ruta/a/tu/capa.shp'
gdf_layer = QgsVectorLayer(shapefile, "Geospatial Layer", "ogr")
if not gdf_layer.isValid():
    print("Error al cargar el shapefile.")
else:
    QgsProject.instance().addMapLayer(gdf_layer)

# Unir las capas
join_field_csv = 'id'  # Campo en el CSV
join_field_gdf = 'id'  # Campo en el shapefile

# Crear la unión
join_info = QgsVectorLayerJoinInfo()
join_info.setJoinLayer(csv_layer)
join_info.setJoinFieldName(join_field_csv)
join_info.setTargetFieldName(join_field_gdf)
join_info.setUsingMemoryCache(True)  # Usar caché en memoria para mejorar el rendimiento

# Añadir la unión a la capa geoespacial
gdf_layer.addJoin(join_info)

# Mostrar el resultado en la tabla de atributos
print("La unión se ha realizado correctamente.")


▎Explicación del código:

1. Importar bibliotecas: Importamos las clases necesarias desde qgis.core.

2. Cargar el archivo CSV: Usamos QgsVectorLayer para cargar el CSV como una capa. Asegúrate de especificar el delimitador correcto (en este caso, una coma).

3. Cargar la capa geoespacial: Cargamos el shapefile de manera similar.

4. Unir las capas: Creamos un objeto QgsVectorLayerJoinInfo para especificar cómo se debe realizar la unión entre las capas.

5. Añadir la unión: Usamos el método addJoin() para agregar la unión a la capa geoespacial.
"""

from abc import ABC, abstractmethod
import csv
import os

from qgis.core import (QgsProject, QgsVectorLayer, QgsLayerTreeLayer, QgsVectorLayerJoinInfo, QgsClassificationQuantile, # type: ignore
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
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer, False)
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
        joinObject.setTargetFieldName("Name")
        joinObject.setJoinLayerId(source_layer.id())
        joinObject.setUsingMemoryCache(True)
        joinObject.setJoinLayer(source_layer)
        joinObject.setJoinFieldNamesSubset(fields_to_add)
        # joinObject.setPrefix(self.analysisExecutionId)
        target_layer.addJoin(joinObject)
        self.changeColor(self.Field)