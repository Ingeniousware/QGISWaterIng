
from ..inpProcessing.sectionINPAbstract import sectionINPAbstract


class sectionVertices(sectionINPAbstract):
    def __init__(self):
            #Constructor.
            super(sectionVertices, self).__init__()  


    def ProcessCoordinatesConvertion(self, out_file, line):
        parts = line.strip().split()
                                     
        if len(parts) >= 3 and parts[0] != "Link" and parts[1] != "X-Coord" and parts[2] != "Y-Coord":
            try:
                node, x_coord, y_coord = parts[0], float(parts[1]), float(parts[2])
                google_latitude, google_longitude = sectionINPAbstract.convert_to_coordinates(self,x_coord, y_coord)
                                
                updated_line = f"{node}\t\t{google_longitude:.6f}\t\t{google_latitude:.6f}\n"
                out_file.write(updated_line + '\n')
            except ValueError:
                out_file.write(line + '\n')
        else:
            out_file.write(line + '\n')