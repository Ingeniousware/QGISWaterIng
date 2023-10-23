import math
import csv

from qgis.core import QgsPointXY

class sensorPlacementFromFile:
    def __init__(self):
        """Constructor."""
        ...    
    
    def read_csv(self, filename):
        node_names = []
        sensors_names = []
        d_values =[]
        with open(filename, 'r') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)
            data = list(reader)
            for row in data:
                if len(row) >= 3:
                    node_names.append(row[1])
                    node_names.append(row[2])
            for row in data:
                if len(row) >= 3:
                    sensors_names.append(row[0])
            for row in data:
                if len(row) >= 3:
                    d_values.append(row[3])
            
        return sensors_names, node_names, d_values

    def update_data_values(self, nodes_list):
        updated_nodes = []
        data_value_idx = 0
        sensor_name_idx =0
        for i, (name, x, y, data, sensor) in enumerate(nodes_list):
            if i % 2 == 0 and i != 0:
                data_value_idx += 1
                sensor_name_idx +=1

            data_value_str = nodes_list[0][3][data_value_idx]
            updated_data_value = float(data_value_str.replace(',', '.'))
            sensor_name = nodes_list[0][4][sensor_name_idx]

            updated_nodes.append((sensor_name, x, y, updated_data_value))
        return updated_nodes
    
    def calculate_distances(self, node_list):
        if len(node_list) % 2 != 0:
            print("The list should have an even number of nodes to calculate pairwise distances.")
            return

        #distances = []
        sensor_coordinates =[]
        for i in range(0, len(node_list), 2):
    
            name1, x1, y1, dist1 = node_list[i][0], node_list[i][1], node_list[i][2], node_list[i][3]
            name2, x2, y2, dist2 = node_list[i+1][0], node_list[i+1][1], node_list[i+1][2], node_list[i+1][3]

            delta_x = x2 - x1
            delta_y = y2 - y1
            
            calculated_distance = math.sqrt((delta_x)**2 + (delta_y)**2)
            delta_x /= calculated_distance
            delta_y /= calculated_distance
            x = x1 + delta_x * dist1
            y = y1 + delta_y * dist1
            my_coord = QgsPointXY(x, y)

            #distances.append((f"{name1}-{name2}", calculated_distance, dist1))
            sensor_coordinates.append((my_coord))     
        return sensor_coordinates