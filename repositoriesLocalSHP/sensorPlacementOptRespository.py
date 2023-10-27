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
        d_values = []
        
        with open(filename, 'r') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)
            for row in reader:
                if len(row) >= 4:  # Ensure there are enough elements in row
                    sensors_names.append(row[0])
                    node_names.extend([row[1], row[2]])  # Using extend to add two items
                    d_values.append(row[3])
            
        return sensors_names, node_names, d_values

    def update_data_values(self, nodes_list):
        updated_nodes = []
        for i, (name, x, y, data, sensor) in enumerate(nodes_list):
            data_value_str = data[i // 2]
            updated_data_value = float(data_value_str.replace(',', '.'))
            sensor_name = sensor[i // 2]

            updated_nodes.append((sensor_name, x, y, updated_data_value))
        
        return updated_nodes

    def calculate_distances(self, node_list):
        if len(node_list) % 2 != 0:
            print("The list should have an even number of nodes to calculate pairwise distances.")
            return

        sensor_coordinates = []
        for i in range(0, len(node_list), 2):
            name1, x1, y1, dist1 = node_list[i]
            _, x2, y2, dist2 = node_list[i+1]

            delta_x, delta_y = x2 - x1, y2 - y1
            calculated_distance = math.sqrt(delta_x**2 + delta_y**2)
            delta_x /= calculated_distance
            delta_y /= calculated_distance
            x = x1 + delta_x * dist1
            y = y1 + delta_y * dist1

            sensor_coordinates.append(QgsPointXY(x, y))

        return sensor_coordinates
