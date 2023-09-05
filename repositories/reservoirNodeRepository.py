import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class ReservoirNodeRepository(AbstractRepository):
    
    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(ReservoirNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "https://dev.watering.online/api/v1/WaterReservoir"
        self.StorageShapeFile = os.path.join(project_path, "watering_reservoirs.shp")
        self.Layer = QgsVectorLayer(self.StorageShapeFile, QFileInfo(self.StorageShapeFile).baseName(), "ogr")


     
    def createElementShp(self):
        #Reservoirs Loading
        response_reservoirs = self.loadElements()
        
        #Setting shapefile fields 
        
        reservoirs_field_definitions = [
        ("Reservoir ID", QVariant.String),
        ("Last Modified", QVariant.String),
        ("Name", QVariant.String),
        ("Description", QVariant.String),
        ("Z[m]", QVariant.Double),
        ("Head[m]", QVariant.Double)
        ]
        
        fields = self.setElementFields(reservoirs_field_definitions)

        new_layer = QgsVectorLayer("Point?crs=" + self.destCrs.authid(), "New Layer", "memory")
        new_layer.dataProvider().addAttributes(fields)
        new_layer.updateFields()
        
        #Adding tanks to shapefile
        list_of_reservoirs = []
        for i in range(0, response_reservoirs.json()["total"]):
            reservoirFeatures = []
            reservoirFeatures.append((response_reservoirs.json()["data"][i]["lng"],
                                      response_reservoirs.json()["data"][i]["lat"]))
            reservoirFeatures.append(response_reservoirs.json()["data"][i]["serverKeyId"])
            reservoirFeatures.append(response_reservoirs.json()["data"][i]["lastModified"])
            reservoirFeatures.append(response_reservoirs.json()["data"][i]["name"])
            reservoirFeatures.append(response_reservoirs.json()["data"][i]["description"])
            reservoirFeatures.append(response_reservoirs.json()["data"][i]["z"])
            reservoirFeatures.append(response_reservoirs.json()["data"][i]["head"])
            list_of_reservoirs.append(reservoirFeatures)


        for reservoir in list_of_reservoirs:
            feature = QgsFeature(new_layer.fields())
            g = QgsGeometry.fromPointXY(QgsPointXY(reservoir[0][0], reservoir[0][1]))
            g.transform(transform)
            feature.setGeometry(g) 
            feature.setAttribute("Reservoir ID", reservoir[1])
            feature.setAttribute("Last Modified", reservoir[2])
            feature.setAttribute("Name", reservoir[3])
            feature.setAttribute("Description", reservoir[4])
            feature.setAttribute("Z[m]", reservoir[5])
            feature.setAttribute("Head[m]", reservoir[6])
            new_layer.dataProvider().addFeature(feature)

        #Writing Shapefile
        writer = QgsVectorFileWriter.writeAsVectorFormat(new_layer, self.reservoirsFile, "utf-8", new_layer.crs(), "ESRI Shapefile")
        if writer[0] == QgsVectorFileWriter.NoError:
            print("Shapefile created successfully!")
        else:
            print("Error creating tanks Shapefile!")
        self.createDemandNodesShp()

    

    def setElementSymbol(self, layer):
        renderer = layer.renderer()
        symbol = renderer.symbol()
        symbol.changeSymbolLayer(0, QgsSimpleMarkerSymbolLayer(QgsSimpleMarkerSymbolLayerBase.Square))
        symbol.setSize(6) 
        symbol.setColor(QColor.fromRgb(23, 61, 108))
        layer.triggerRepaint()
