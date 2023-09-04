import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class WateringDemandNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(WateringDemandNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "https://dev.watering.online/api/v1/DemandNode"
        self.StorageShapeFile = os.path.join(project_path, "watering_demand_nodes.shp")
        self.Layer = QgsVectorLayer(self.StorageShapeFile, QFileInfo(self.StorageShapeFile).baseName(), "ogr")


    def setElementFields(self):
        fields = QgsFields()
        fields.append(QgsField("Demand Node ID", QVariant.String))
        fields.append(QgsField("Last Modified", QVariant.String))
        fields.append(QgsField("Name", QVariant.String))
        fields.append(QgsField("Description", QVariant.String))
        fields.append(QgsField("Z[m]", QVariant.Double))
        fields.append(QgsField("Base Demand [l/s]", QVariant.Double))
        fields.append(QgsField("Demand Pattern", QVariant.Bool))
        return fields
    

    def createElementShp(self):
        #Water Demands Loading
        response_demand_nodes = self.loadElements()
        
        #Setting shapefile fields 
        fields = self.setElementFields()
        
        sourceCrs = QgsCoordinateReferenceSystem(4326)
        destCrs = QgsCoordinateReferenceSystem(3857)
        transform = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
        
        new_layer = QgsVectorLayer("Point?crs=" + destCrs.authid(), "New Layer", "memory")
        new_layer.dataProvider().addAttributes(fields)
        new_layer.updateFields()
        
        #Adding tanks to shapefile
        list_of_demand_nodes = []
        for i in range(0, response_demand_nodes.json()["total"]):
            demandNodeFeatures = []
            demandNodeFeatures.append((response_demand_nodes.json()["data"][i]["lng"],
                                         response_demand_nodes.json()["data"][i]["lat"]))
            demandNodeFeatures.append(response_demand_nodes.json()["data"][i]["serverKeyId"])
            demandNodeFeatures.append(response_demand_nodes.json()["data"][i]["lastModified"])
            demandNodeFeatures.append(response_demand_nodes.json()["data"][i]["name"])
            demandNodeFeatures.append(response_demand_nodes.json()["data"][i]["description"])
            demandNodeFeatures.append(response_demand_nodes.json()["data"][i]["z"])
            demandNodeFeatures.append(response_demand_nodes.json()["data"][i]["baseDemand"])
            demandNodeFeatures.append(response_demand_nodes.json()["data"][i]["demandPatternFK"])
            list_of_demand_nodes.append(demandNodeFeatures)

        for demand_node in list_of_demand_nodes:
            feature = QgsFeature(new_layer.fields())
            g = QgsGeometry.fromPointXY(QgsPointXY(demand_node[0][0], demand_node[0][1]))
            g.transform(transform)
            feature.setGeometry(g) 
            feature.setAttribute("Demand Node ID", demand_node[1])
            feature.setAttribute("Last Modified", demand_node[2])
            feature.setAttribute("Name", demand_node[3])
            feature.setAttribute("Description", demand_node[4])
            feature.setAttribute("Z[m]", demand_node[5])
            feature.setAttribute("Base Demand [l/s]", demand_node[6])
            feature.setAttribute("Demand Pattern", demand_node[7])
            new_layer.dataProvider().addFeature(feature)

        #Writing Shapefile
        writer = QgsVectorFileWriter.writeAsVectorFormat(new_layer, self.StorageShapeFile, "utf-8", new_layer.crs(), "ESRI Shapefile")
        if writer[0] == QgsVectorFileWriter.NoError:
            print("Shapefile created successfully!")
        else:
            print("Error creating tanks Shapefile!")


    def setElementSymbol(self):
        renderer = layer.renderer()
        symbol = renderer.symbol()
        symbol.changeSymbolLayer(0, QgsSimpleMarkerSymbolLayer(QgsSimpleMarkerSymbolLayerBase.Circle))
        symbol.setSize(3) 
        symbol.setColor(QColor.fromRgb(23, 61, 108))
        self.Layer.triggerRepaint()