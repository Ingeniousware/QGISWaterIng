
from ..inpProcessing.sectionINPAbstract import sectionINPAbstract
from qgis.core import QgsCoordinateReferenceSystem

class sectionVertices(sectionINPAbstract):
    def __init__(self, sourceCrs=QgsCoordinateReferenceSystem(4326)):
            #Constructor.
            super(sectionVertices, self).__init__(sourceCrs)  


    def ProcessCoordinatesConvertion(self, out_file, line):
        parts = line.strip().split()
                                     
        if len(parts) >= 3:
            try:
                node, x_coord, y_coord = parts[0], float(parts[1]), float(parts[2])
                google_latitude, google_longitude = self.convert_to_coordinates(x_coord, y_coord)
                                
                updated_line = f"{node}\t\t{google_longitude:.6f}\t\t{google_latitude:.6f}"
                out_file.write(updated_line + '\n')
            except ValueError:
                out_file.write(line + '\n')
        else:
            out_file.write(line + '\n')