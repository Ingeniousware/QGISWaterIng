import os
import requests
from repositories.abstract_repository import AbstractRepository


class TankNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(TankNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "https://dev.watering.online/api/v1/TankNode"
        self.StorageShapeFile = os.path.join(project_path, "watering_tanks.shp")
        self.Layer = QgsVectorLayer(self.StorageShapeFile, QFileInfo(self.StorageShapeFile).baseName(), "ogr")

             
    def setElementFields(self):
        fields = QgsFields()
        fields.append(QgsField("Tank ID", QVariant.String))
        fields.append(QgsField("Last Modified", QVariant.String))
        fields.append(QgsField("Name", QVariant.String))
        fields.append(QgsField("Description", QVariant.String))
        fields.append(QgsField("Z[m]", QVariant.Double))
        fields.append(QgsField("Initial Level [m]", QVariant.Double))
        fields.append(QgsField("Minimum Level [m]", QVariant.Double))
        fields.append(QgsField("Maximum Level [m]", QVariant.Double))
        fields.append(QgsField("Minimum Volume [m3]", QVariant.Double))
        fields.append(QgsField("Diameter", QVariant.Double))
        fields.append(QgsField("Can Overflow", QVariant.Bool))
        return fields
     
    def createElementShp(self):
        #Tanks Loading
        response_tanks = self.loadElements()
        
        #Setting shapefile fields 
        fields = self.setElementFields()
        
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

    

    def setElementSymbol(self, layer):
        renderer = layer.renderer()
        symbol = renderer.symbol()
        symbol.changeSymbolLayer(0, QgsSimpleMarkerSymbolLayer(QgsSimpleMarkerSymbolLayerBase.Pentagon))
        symbol.setSize(6) 
        symbol.setColor(QColor.fromRgb(23, 61, 108))
        layer.triggerRepaint()