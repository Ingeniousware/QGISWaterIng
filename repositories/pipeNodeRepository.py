import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsLayerTreeLayer
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsSymbol, edit
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class PipeNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(PipeNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/WaterPipe"
        self.StorageShapeFile = os.path.join(project_path, "watering_pipes.shp")
        self.LayerName = "watering_pipes"
        self.field_definitions = None
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.initializeRepository()

    def initializeRepository(self):
        #Pipes loading
        response_pipes = self.loadElements()
        
        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Diameter [m]", QVariant.Double),
            ("Length [m]", QVariant.Double),
            ("Roughness (absol) [mm]", QVariant.Double),
            ("Rough.Coeff.(H.W.)", QVariant.Double),
            ("Up-Node", QVariant.String),
            ("Down-Node", QVariant.String),
            ("C Status", QVariant.Double),
            ("Velocity", QVariant.Double),
            ("Flow", QVariant.Double),
            ("HeadLoss", QVariant.Double)
        ]
        
        pipe_attributes = ["serverKeyId", "lastModified", "name", "description", "diameterInt",
                           "length", "roughnessAbsolute", "roughnessCoefficient", "nodeUpName", "nodeDownName",
                           "pipeCurrentStatus","velocity", "flow" ,"headLoss"]
        
        fields = self.setElementFields(self.field_definitions)
        
        layer = QgsVectorLayer("LineString", "Line Layer", "memory")
        layer_provider = layer.dataProvider()
        layer_provider.addAttributes(fields)
        layer.updateFields()
        
        #Adding tanks to shapefile
        for pipe in response_pipes.json()["data"]:
            pipe.update({'pipeCurrentStatus': 0, 'velocity': 0, 'flow': 0, 'headLoss': 0})
            feature = QgsFeature(layer.fields())
            points = [QgsPointXY(vertex['lng'], vertex['lat']) for vertex in pipe["vertices"]]
            g = QgsGeometry.fromPolylineXY(points)
            feature.setGeometry(g)
            for field, attribute in zip(self.field_definitions, pipe_attributes):
                feature.setAttribute(field[0], pipe[attribute])
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
        symbol_layer.setWidth(0.7)
        layer.renderer().setSymbol(symbol)


        root = QgsProject.instance().layerTreeRoot()


        shapeGroup = root.findGroup("WaterIng Network Layout")

        #print(foundshapeGroup)        
        #shapeGroup = root.addGroup("WaterIng Network Layout")

        

        shapeGroup.insertChildNode(1, QgsLayerTreeLayer(layer))

        QgsProject.instance().addMapLayer(layer, False)
