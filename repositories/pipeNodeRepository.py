import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsSymbol
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class PipeNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(PipeNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "https://dev.watering.online/api/v1/WaterPipe"
        self.StorageShapeFile = os.path.join(project_path, "watering_pipes.shp")
        self.pipesLayer()
     
    def pipesLayer(self):
        #Pipes loading
        response_pipes = self.loadElements()
        
        #Setting shapefile fields 
        pipe_field_definitions = [
            ("Pipe ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Diameter [m]", QVariant.Double),
            ("Length [m]", QVariant.Double),
            ("Roughness (absol) [mm]", QVariant.Double),
            ("Rough.Coeff.(H.W.)", QVariant.Double),
            ("Up-Node", QVariant.String),
            ("Down-Node", QVariant.String),
        ]
        
        #pipe_features = ["lng", "lat", "serverKeyId","lastModified","name", "description", "z","initialLevel",
        #                 "minimumLevel","maximumLevel","minimumVolume", "nominalDiameter","canOverflow"]
        
        fields = self.setElementFields(pipe_field_definitions)
        
        layer = QgsVectorLayer("LineString", "Line Layer", "memory")
        layer_provider = layer.dataProvider()
        layer_provider.addAttributes(fields)
        layer.updateFields()
        
        #Adding tanks to shapefile
        list_of_pipes = []
        response_data = response_pipes.json()["data"]
        for pipe in response_data:
            pipe_features = [
               (pipe["vertices"][0]["lng"], pipe["vertices"][0]["lat"]),
                (pipe["vertices"][1]["lng"], pipe["vertices"][1]["lat"]),
                pipe["serverKeyId"],
                pipe["lastModified"],
                pipe["name"],
                pipe["description"],
                pipe["diameterInt"],
                pipe["length"],
                pipe["roughnessAbsolute"],
                pipe["roughnessCoefficient"],
                pipe["nodeUpName"],
                pipe["nodeDownName"]
            ]
            list_of_pipes.append(pipe_features)
        
        for pipe in list_of_pipes:
            feature = QgsFeature(layer.fields())
            point1 = QgsPointXY(pipe[0][0], pipe[0][1])
            point2 = QgsPointXY(pipe[1][0], pipe[1][1])
            points = [point1, point2]
            g = QgsGeometry.fromPolylineXY(points)
            feature.setGeometry(g)
            feature.setAttribute("Pipe ID", pipe[2])
            feature.setAttribute("Last Modified", pipe[3])
            feature.setAttribute("Name", pipe[4])
            feature.setAttribute("Description", pipe[5])
            feature.setAttribute("Diameter [m]", pipe[6])
            feature.setAttribute("Length [m]", pipe[7])
            feature.setAttribute("Roughness (absol) [mm]", pipe[8])
            feature.setAttribute("Rough.Coeff.(H.W.)", pipe[9])
            feature.setAttribute("Up-Node", pipe[10])
            feature.setAttribute("Down-Node", pipe[11])
            print(feature.attributes)
            layer_provider.addFeature(feature)
         
        writer = QgsVectorFileWriter.writeAsVectorFormat(layer, self.StorageShapeFile, "utf-8", self.destCrs, "ESRI Shapefile")
        if writer[0] == QgsVectorFileWriter.NoError:
            print("Shapefile created successfully!")
        else:
            print("Error creating pipes Shapefile!")
        
        layer = QgsVectorLayer(self.StorageShapeFile, QFileInfo(self.StorageShapeFile).baseName(), "ogr")

        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol_layer = symbol.symbolLayer(0)
        symbol_layer.setColor(QColor.fromRgb(13, 42, 174))
        symbol_layer.setWidth(1)
        layer.renderer().setSymbol(symbol)

        QgsProject.instance().addMapLayer(layer)