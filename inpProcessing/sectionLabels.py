
from ..inpProcessing.sectionINPAbstract import sectionINPAbstract


class sectionLabels(sectionINPAbstract):
    def __init__(self):
            #Constructor.
            super(sectionLabels, self).__init__()  


    def ProcessCoordinatesConvertion(self, out_file, line):
        parts = line.strip().split()
                                       
    
        try:
            x_coord, y_coord = float(parts[0]), float(parts[1])
            google_latitude, google_longitude = sectionINPAbstract.convert_to_coordinates(self,x_coord, y_coord)
                            
            updated_line = f"{google_longitude:.6f}\t\t{google_latitude:.6f}\t{parts[2]}\n"
            out_file.write(updated_line + '\n')
        except ValueError:
            out_file.write(line + '\n')
    