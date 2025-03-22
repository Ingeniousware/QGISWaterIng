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
import io
import json
import os

from qgis.core import (QgsProject, QgsVectorLayer, QgsLayerTreeLayer, QgsVectorLayerJoinInfo, QgsClassificationQuantile, # type: ignore
                       QgsRendererRangeLabelFormat, QgsStyle, QgsGradientColorRamp, QgsGraduatedSymbolRenderer)
from qgis.PyQt.QtGui import QColor # type: ignore

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

        source_layer = None
        target_layer = None
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



#==================================================================================================
class AbstractAnalysis_1(ABC):
    """ES - Clase base que establece los métodos y atributos necesarios para la carga y representación de datos
    provenientes de archivos CSV en QGIS.

    EN - Base class that establishes the methods and attributes needed to load and represent data from CSV files in QGIS.
    from CSV files into QGIS."""
    def __init__(self, directoryBase, analysisExecutionId, datetime):
        """Constructor for Abstract Analysis

        Parameters
        ----------
        directoryBase : str
            ES - ID del análisis ejecutado (GUID).

            EN - ID of the executed analysis (GUID).

        analysisExecutionId : str
            ES - ID del análisis ejecutado (GUID).

            EN - ID of the executed analysis (GUID).

        datetime : str
            ES - Hora en la que se ejecuta el análisis.

            EN - Time at which the analysis is run.
        """
        super().__init__()
        self.DirectoryBase = directoryBase
        """Representa el direcyorio base para generar los archovos de la simulación."""
        self.AnalysisExecutionId = analysisExecutionId
        self.Datetime = datetime
        self.__dataTimeStr = self.Datetime.translate(str.maketrans({":": "-", ".": "-"}))
        self.__jsonFileName = "analysis.json"

        self.LayerName = None
        self.StartColor = QColor(55, 148, 255)
        self.EndColor = QColor(255, 47, 151)
        self.Size = 1
        self.Field = None
        self.CsvDirectory = None
        self.LayerNameCsv = None
        self.CsvFileName = None
        self.JoinField = None
        self.FieldsToAdd = None
       
        self.ShapeGroup_for_Analysis = "Analysis"
        """Representa la capa donde se agrupan los análisis."""


    @property
    def LayerName(self)->str:
        """ES - Obtiene o estable el nombre de la capa donde se va a juntar el archivo CSV.

        EN - Gets or sets the name of the layer where the CSV file is to be joined."""
        return self.__layerName
    @LayerName.setter
    def LayerName(self, value: str):
        self.__layerName = value


    @property
    def StartColor(self):
        """ES - Obtiene o estable el color de inicio.

        EN - Gets or sets the color to start"""
        return self.__startColor
    @StartColor.setter
    def StartColor(self, value):
        self.__startColor = value


    @property
    def EndColor(self):
        """ES - Obtiene o estable el color de final.

        EN - Gets or sets the end color"""
        return self.__endColor
    @EndColor.setter
    def EndColor(self, value):
        self.__endColor = value


    @property
    def Size(self):
        """ES - Obtiene o estable el tamaño de la capa.

        EN - Gets or sets the layer size"""
        return self.__size
    @Size.setter
    def Size(self, value):
        self.__size = value


    @property
    def Field(self)->str:
        """ES - Obtiene o estable el nombre del campo que se va a visulizar en la tabla de atributos.

        EN - Gets or sets the name of the field to be displayed in the attribute table."""
        return self.__field
    @Field.setter
    def Field(self, value: str):
        self.__field = value


    @property
    def CsvDirectory(self)->str:
        """ES - Obtiene o estable la ruta donde se encuentra el archivo CSV.

        EN - Gets or sets the path where the CSV file is located."""

        if (self.DirectoryBase is None):
            working_directory = INP_Utils.default_working_directory()
            date_folder_path = os.path.join(working_directory, self.ShapeGroup_for_Analysis, self.__dataTimeStr)
            self.__csvDirectory = INP_Utils.generate_directory(date_folder_path)
        else:
            self.__csvDirectory = self.DirectoryBase

        return self.__csvDirectory
    @CsvDirectory.setter
    def CsvDirectory(self, value: str):
        self.__csvDirectory = value


    @property
    def LayerNameCsv(self)-> str:
        """ES - Obtiene o estable el nombre del layer que se va a crear a partir del archivo CSV.

        EN - Gets or sets the name of the layer to be created from the CSV file."""

        if (self.__layerNameCsv is None):
            if ("nodes" in self.LayerName.lower()):
                self.__layerNameCsv = f"Node_{self.__dataTimeStr}"
            elif ("pipes" in self.LayerName.lower()):
                self.__layerNameCsv = f"Pipes_{self.__dataTimeStr}"

        return self.__layerNameCsv
    @LayerNameCsv.setter
    def LayerNameCsv(self, value: str):
        self.__layerNameCsv = value


    @property
    def CsvFileName(self)-> str:
        """ES - Obtiene o estable el nombre del archivo CSV.

        EN - Gets or sets the CSV file name."""

        if (self.__csvFileName is None):
            if ("nodes" in self.LayerName.lower()):
                self.__csvFileName = f"{self.AnalysisExecutionId}_Node.csv"
            elif ("pipes" in self.LayerName.lower()):
                self.__csvFileName = f"{self.AnalysisExecutionId}_Pipes.csv"

        return self.__csvFileName
    @CsvFileName.setter
    def CsvFileName(self, value: str):
        self.__csvFileName = value


    @property
    def JoinField(self)->str:
        """ES - Llave por la cual se van a juntar los datos del archivo CSV con la capa.

        En - Key by which the data from the CSV file will be merged with the layer."""
        return self.__joinField
    @JoinField.setter
    def JoinField(self, value: str):
        self.__joinField = value


    @property
    def FieldsToAdd(self)->list:
        """ES - Campos que adiciona a los atributos de la capa.

        EN - Fields you add to the layer attributes."""
        return self.__fieldsToAdd
    @FieldsToAdd.setter
    def FieldsToAdd(self, value: list):
        self.__fieldsToAdd = value


    @abstractmethod
    def elementAnalysisResultsDisplayed(self):
         """ES - Método donde se implementa la lógica para generar el archivo CSV.

         EN - Method where the logic to generate the CSV file is implemented."""
         pass


    @abstractmethod
    def elementAnalysisResults(self, result_csv, analysisExecutionId):
        """ES - Método donde se implementa la lógica para generar el archivo CSV.

        EN - Method where the logic to generate the CSV file is implemented.

        Parameters
        ----------
        analysisExecutionId : str
            ES - ID del análisis ejecutado (GUID).

            EN - ID of the executed analysis (GUID).

        result_csv : any
            ES - Resulatos que se van a guardar en un archivo CSV.

            EN - Results to be saved in a CSV file.
        """
        pass


    def Execute(self):
        """ËS - "Método que implementa la lógica para mostrar la información en la capa.

        EN - Method that implements the logic for displaying information in the layer."""
        self.elementAnalysisResultsDisplayed()
        self.addCSVNonSpatialLayerToPanel()
        self.joinLayersAttributes()


    def loadCSVLayer(self, group):
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
        filepath = os.path.join(self.CsvDirectory, self.CsvFileName)
        uri = f"file:///{filepath}?type=csv&delimiter=,&detectTypes=yes&geomType=none"
        # Crear la capa desde el archivo CSV
        layer = QgsVectorLayer(uri, self.LayerNameCsv, "delimitedtext")
        if layer.isValid():
            # Añadir la capa al proyecto sin hacerla visible inmediatamente
            QgsProject.instance().addMapLayer(layer, False)
            # Agregar la capa al grupo
            group.addChildNode(QgsLayerTreeLayer(layer))
        else:
            print(f"{self.LayerNameCsv} failed to load! Error: {layer.error().message()}")


    def addCSVNonSpatialLayerToPanel(self):
        """
        Agrega un layer no espacial a la ventana de resultados a partir de un fichero CSV.

        Parameters
        ----------
        fileName: str
            Nombre del fichero.
        layerName: str
            Nombre del layer no espacial.
        """
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup(self.ShapeGroup_for_Analysis)
        if not shapeGroup:
            shapeGroup = root.addGroup(self.ShapeGroup_for_Analysis)

        self.loadCSVLayer(shapeGroup)


    def changeColor(self):
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

        if (self.LayerName is not None):
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
        else:
            print("El nombre del layer es None, este valor no puede ser None")


    def joinLayersAttributes(self):
        """
        Método a junata el layes con los attributes especificados.

        Parameters
        ----------
        join_field:
            Campo por el se va a efectuar la union.
        fields_to_add:
            Campos que se van a adicionar.
        """

        source_layer = None
        target_layer = None
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == self.LayerNameCsv:
                source_layer = layer
            if layer.name() == self.LayerName:
                target_layer = layer
        if not source_layer or not target_layer:
            raise ValueError("One or both layers not found in the project!")

        joinObject = QgsVectorLayerJoinInfo()
        joinObject.setJoinFieldName(self.JoinField)
        joinObject.setTargetFieldName("ID")
        joinObject.setJoinLayerId(source_layer.id())
        joinObject.setUsingMemoryCache(True)
        joinObject.setJoinLayer(source_layer)
        joinObject.setJoinFieldNamesSubset(self.FieldsToAdd)
        target_layer.addJoin(joinObject)
        self.changeColor()


    def removerAnalysis(self):
         # Seeliminan los layes que se crearon para motrar los resultados
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup(self.ShapeGroup_for_Analysis)
        if shapeGroup:
            layer_ids = [layer.layerId() for layer in shapeGroup.findLayers()]
            root.removeChildNode(shapeGroup)
            for layer_id in layer_ids:
                QgsProject.instance().removeMapLayer(layer_id)
    
    
    def updateData(self, analysisExecutionId, time_for_analysis):
        """
        ES - Método que actualiza los datos de las simulaciones en JSON.

        EN - Method that updates simulation data in JSON.

        Parameters
        ----------
        analysisExecutionId : str
            ES - ID del análisis ejecutado (GUID).

            EN - ID of the executed analysis (GUID).

        time_for_analysis: int
            ES - Hora del análisis.

            EN - Hour of the analysis.
        """
        file_path = os.path.join(self.CsvDirectory, self.__jsonFileName)
        typeElement = ""
        if ("nodes" in self.LayerName.lower()):
            typeElement = "Node"
        elif ("pipes" in self.LayerName.lower()):
            typeElement = "Pipes"

        propertyElement = self.Field.split("_")[-1]

        contenido = None
        try:
            with open(file_path, "r") as f:
                contenido = json.load(f)
            contenido.append({"hora": time_for_analysis,
                "type": typeElement,
                "property": propertyElement,
                "id": analysisExecutionId,
                "datetime": self.Datetime,
                "directoryBase": self.CsvDirectory})
            with open(file_path, "w") as f:
                json.dump(contenido, f, indent=4)
        except FileNotFoundError:
            contenido = [
                {"hora": time_for_analysis,
                "type": typeElement,
                "property": propertyElement,
                "id": analysisExecutionId,
                "datetime": self.Datetime,
                "directoryBase": self.CsvDirectory}]
            with open(file_path, "w") as f:
                json.dump(contenido, f, indent=4)