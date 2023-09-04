import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class TankNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(TankNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "https://dev.watering.online/api/v1/TankNode"
        self.StorageShapeFile = os.path.join(project_path, "watering_tanks.shp")
        self.Layer = QgsVectorLayer(self.StorageShapeFile, QFileInfo(self.StorageShapeFile).baseName(), "ogr")
        self.createElementShp()
     
    def createElementShp(self):
        #Tanks Loading
        response_tanks = self.loadElements()

        tank_field_definitions = [
            ("Tank ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Initial Level [m]", QVariant.Double),
            ("Minimum Level [m]", QVariant.Double),
            ("Maximum Level [m]", QVariant.Double),
            ("Minimum Volume [m3]", QVariant.Double),
            ("Diameter", QVariant.Double),
            ("Can Overflow", QVariant.Bool)
        ]
        
        
        #Setting shapefile fields 
        fields = self.setElementFields(tank_field_definitions)
        
        sourceCrs = QgsCoordinateReferenceSystem(4326)
        destCrs = QgsCoordinateReferenceSystem(3857)
        transform = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
        
        new_layer = QgsVectorLayer("Point?crs=" + destCrs.authid(), "New Layer", "memory")
        new_layer.dataProvider().addAttributes(fields)
        new_layer.updateFields()
        
        #Adding tanks to shapefile
        list_of_tanks = []
        response_data = response_tanks.json()["data"]
        for tank in response_data:
            tank_features = [
                (tank["lng"], tank["lat"]),
                tank["serverKeyId"],
                tank["lastModified"],
                tank["name"],
                tank["description"],
                tank["z"],
                tank["initialLevel"],
                tank["minimumLevel"],
                tank["maximumLevel"],
                tank["minimumVolume"],
                tank["nominalDiameter"],
                tank["canOverflow"]
            ]
            list_of_tanks.append(tank_features)
        
        for tank in list_of_tanks:
            feature = QgsFeature(new_layer.fields())
            g = QgsGeometry.fromPointXY(QgsPointXY(tank[0][0], tank[0][1]))
            g.transform(transform)
            feature.setGeometry(g) 
            feature.setAttribute("Tank ID", tank[1])
            feature.setAttribute("Last Modified", tank[2])
            feature.setAttribute("Name", tank[3])
            feature.setAttribute("Description", tank[4])
            feature.setAttribute("Z[m]", tank[5])
            feature.setAttribute("Initial Level [m]", tank[6])
            feature.setAttribute("Minimum Level [m]", tank[7])
            feature.setAttribute("Maximum Level [m]", tank[8])
            feature.setAttribute("Minimum Volume [m3]", tank[9])
            feature.setAttribute("Diameter", tank[10])
            feature.setAttribute("Can Overflow", tank[11])
            new_layer.dataProvider().addFeature(feature)

        #Writing Shapefile
        writer = QgsVectorFileWriter.writeAsVectorFormat(new_layer, self.StorageShapeFile, "utf-8", new_layer.crs(), "ESRI Shapefile")
        if writer[0] == QgsVectorFileWriter.NoError:
            print("Shapefile created successfully!")
        else:
            print("Error creating tanks Shapefile!")
        
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Pentagon, 6)
    