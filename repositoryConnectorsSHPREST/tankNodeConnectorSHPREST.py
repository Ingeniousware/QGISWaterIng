import os
import requests

from .abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST
from ..watering_utils import WateringUtils

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
import queue
import uuid

class tankNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self, scenarioFK, connectionHub):
        """Constructor."""
        super(tankNodeConnectorSHPREST, self).__init__(scenarioFK)    
        self.serverRepository = None  
        self.localRepository = None
        connectionHub.on("POST_TANK", self.processPOSTElementToLocal)
        connectionHub.on("DELETE_TANK", self.processDELETEElementToLocal)
        self.lastAddedElements = {}
        self.lifoAddedElements = queue.LifoQueue()

    def processPOSTElementToLocal(self, paraminput):
        print("Entering processPOSTElementToLocal")        
        #print(paraminput[0])
        jsonInput = paraminput[0]
        serverKeyId = jsonInput["serverKeyId"]
        print(serverKeyId)
        if not (serverKeyId in self.lastAddedElements):
            self.localRepository.addElementFromSignalR(paraminput[0])
            print("Water Tank Node inserted after push from server")
            print("dict-> ", self.lastAddedElements)
        else:
            print("Key found -> ", serverKeyId)


    def processDELETEElementToLocal(self, paraminput):
        self.localRepository.deleteElement(paraminput[0])
        print("Water Tank Node removed after push from server")


    def addElementToServer(self, feature):
        feature_id = feature.id()
        print("feature id: ", feature_id)

        x = feature.geometry().asPoint().x()
        y = feature.geometry().asPoint().y()
        #transforming coordinates for the CRS of the server
        transGeometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))
        transGeometry.transform(QgsCoordinateTransform(self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance()))
        x = transGeometry.asPoint().x()
        y = transGeometry.asPoint().y()
        
        isNew = False
        if len(feature["ID"]) == 10:
            isNew = True
            serverKeyId = str(uuid.uuid4())
        else:
            serverKeyId = feature["ID"]
            
        print("isNEW: ", isNew)
            
        print("reach 1")
        name = feature["Name"]
        description = feature["Descript"]
        z = feature["Z[m]"]
        initialLevel = feature["Init. Lvl"]
        minimumLevel = feature["Min. Lvl"]
        maximumLevel = feature["Max. Lvl"]
        minimumVolume = feature["Min. Vol."]
        nominalDiameter = feature["Diameter"]
        #canOverflow = feature["Overflow"] == 1 For later tests
        canOverflow = True
        
        #serverKeyId = feature["ID"]
        print("reach 2")
        elementJSON = {'serverKeyId': "{}".format(serverKeyId), 
                       'scenarioFK': "{}".format(self.ScenarioFK), 
                       'name': "{}".format(name), 
                       'description': "{}".format(description), 
                       'lng': "{}".format(x), 
                       'lat': "{}".format(y), 
                       'z': "{}".format(z), 
                       'initialLevel': "{}".format(initialLevel),
                       'minimumLevel': "{}".format(minimumLevel),
                       'maximumLevel': "{}".format(maximumLevel),
                       'minimumVolume':"{}".format(minimumVolume),
                       'nominalDiameter':"{}".format(nominalDiameter),
                       'canOverflow':"{}".format(canOverflow)
                        }
        
        print("element json tanks: ", elementJSON)
        
        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)

        """isNew = False
        if (feature["Last Mdf"] == None): 
            isNew = True"""
            
        #isNew = WateringUtils.getFeatureIsNewStatus(serverKeyId)
        
        if (isNew): 
            print("tank is new, posting")
            serverResponse = self.serverRepository.postToServer(elementJSON)
        else: 
            print("tank is not new, putting")
            serverResponse = self.serverRepository.putToServer(elementJSON, serverKeyId)
        
        #layer = QgsProject.instance().mapLayersByName("watering_tanks")[0]
        
        if serverResponse.status_code == 200:
            print("Water Tank Node was sent succesfully to the server")
            #WateringUtils.setProjectMetadata(serverKeyId, "already on server")
            
            #layer = feature.layer()
            #print("LAYER ON UPDATE LAST UPDATE: ", self.Layer)
            #isNew = True
            #serverKeyId = uuid.uuid4()
            #now = WateringUtils.getDateTimeNow()
            
            #old
            """layer = QgsProject.instance().mapLayersByName("watering_tanks")[0]
            id_feature = feature.id()
            layer.startEditing()
            id_index = layer.fields().indexFromName('ID')
            new_id = str(serverKeyId)
            #feature.setAttribute(layer.fields().indexFromName('ID'), str(serverKeyId))
            layer.changeAttributeValue(id_feature, id_index, new_id)
            print(layer, "id changed ", serverKeyId)
            #feature.setAttribute(self.Layer.fields().indexFromName('lastUpdate'), now)
            layer.updateFeature(feature)
            layer.commitChanges()"""
            
            """#new
            print("isNew: ", isNew)
            if isNew:
                #layer = QgsVectorLayer('/Users/vmstar/Library/Application Support/QGISWatering/22fbb771-0e96-4357-b1b7-d6e045fddc42/watering_tanks.shp', 'watering_tanks', 'ogr')

                #print("layer : ", layer)
                layer = QgsProject.instance().mapLayersByName("watering_tanks")[0]
                
                #prov = layer.dataProvider()
                
                id_element = feature["ID"]
                print("ID EEMENT: ", id_element)
                #layer.startEditing()
                layer.startEditing()

                # Assuming you know the feature's ID or some other unique identifier
                
                id_index = layer.fields().indexFromName('ID')
                print(feature_id)
                # Retrieve the feature with the specified ID
                the_feature = None
                for feat in layer.getFeatures():
                    if feat["ID"] == id_element:
                        the_feature = feat
                        print("Feature Found")
                        break

                # Check if the feature was found
                if the_feature:
                    print("feature id ", the_feature.id())
                    new_s = str(serverKeyId)
                    print("new s: ", new_s)
                    if layer.changeAttributeValue(the_feature.id(), id_index, new_s):
                        print("VALUE CHANGED")
                    else:
                        print("value not changed")
                    layer.updateFeature(the_feature)
                    layer.commitChanges()
                    layer.triggerRepaint()
                else:
                    print("Feature not found")"""
                
                #new
            print("isNew: ", isNew)
            if isNew:
                #layer = QgsVectorLayer('/Users/vmstar/Library/Application Support/QGISWatering/22fbb771-0e96-4357-b1b7-d6e045fddc42/watering_tanks.shp', 'watering_tanks', 'ogr')

                #print("layer : ", layer)
                layer = QgsProject.instance().mapLayersByName("watering_tanks")[0]
                
                prov = layer.dataProvider()
                
                id_element = feature["ID"]
                print("ID EEMENT: ", id_element)
                #layer.startEditing()
                layer.startEditing()

                # Assuming you know the feature's ID or some other unique identifier
                new_s = str(serverKeyId)
                id_index = prov.fields().indexFromName('ID')
                print(feature_id)
                # Retrieve the feature with the specified ID
                the_feature = None
                for feat in prov.getFeatures():
                    if feat["ID"] == id_element:
                        the_feature = feat
                        the_feature.setAttribute(the_feature.fieldNameIndex("ID"), new_s)
                        # Update the feature
                        layer.updateFeature(the_feature)
                        print("Feature Found")
                        break
                
                layer.commitChanges()
                
                """# Check if the feature was found
                if the_feature:
                    print("feature id ", the_feature.id())
                    new_s = str(serverKeyId)
                    print("new s: ", new_s)
                    if prov.changeAttributeValue(the_feature.id(), id_index, new_s):
                        print("VALUE CHANGED")
                    else:
                        print("value not changed")
                    prov.updateFeature(the_feature)
                    layer.commitChanges()
                    layer.triggerRepaint()
                else:
                    print("Feature not found")"""
                    
                """fields = layer.fields()
                
                lastModified_index = fields.indexFromName('Last Mdf')
                
                layer.changeAttributeValue(feature.id(), lastModified_index, WateringUtils.getDateTimeNow())"""
            #writing the server key id to the element that has been created
            #serverKeyId = serverResponse.json()["serverKeyId"]
            #print(serverKeyId)       
            #feature.setAttribute("ID", serverKeyId)   
            if not serverKeyId in self.lastAddedElements:     
                self.lastAddedElements[serverKeyId] = 1
                self.lifoAddedElements.put(serverKeyId)
                while self.lifoAddedElements.full():
                    keyIdToEliminate = self.lifoAddedElements.get()
                    self.lastAddedElements.pop(keyIdToEliminate) 
        else: 
            print("Failed on sendig Water Tank Node to the server. Status Code: ", serverResponse.status_code, " text: ", serverResponse.text)

    

    def removeElementFromServer(self, serverKeyId):
        elementJSON = {'scenarioFK': "{}".format(self.ScenarioFK), 
                       'serverKeyId': "{}".format(serverKeyId)}
        
        serverResponse = self.serverRepository.deleteFromServer(elementJSON)
    