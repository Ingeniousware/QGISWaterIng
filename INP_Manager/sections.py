# -*- coding: utf-8 -*-

"""
***************************************************************************
    sections.py
    ---------------------
    Date                 : Nomviembre 2024
    Copyright            : (C) 2024 by Ingeniowarest
    Email                : 
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Ingenioware                                                       *
*                                                                         *
***************************************************************************
"""




from .inp_options_enum import INP_Options
from .sectionAbstract import sectionAbstract
# from __future__ import annotations
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from .INPManager import INPManager

# Section Title [TITLE] =================================================================
class sectionTitle(sectionAbstract):
    def __init__(self, inpM, title=""):
        super(sectionTitle, self).__init__(inpM, 1)
        self.name = '[TITLE]'
        self.title = title if title is not None else ""
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(' ' + self.title + '\n\n')

# Section Junctions [JUNCTIONS] =================================================================
class sectionJunctions(sectionAbstract):
    def __init__(self, inpM):
        super(sectionJunctions, self).__init__(inpM, 2)
        self.name = '[JUNCTIONS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';ID              	Elev        	Demand      	Pattern         ' + '\n')

        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Reservoirs [RESERVOIRS] =================================================================
class sectionReservoirs(sectionAbstract):
    def __init__(self, inpM):
        super(sectionReservoirs, self).__init__(inpM, 3)
        self.name = '[RESERVOIRS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';ID              	Head        	Pattern         ' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Tanks [TANKS] =================================================================
class sectionTanks(sectionAbstract):
    def __init__(self, inpM):
        super(sectionTanks, self).__init__(inpM, 4)
        self.name = '[TANKS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';ID              	Elevation   	InitLevel   	MinLevel    	MaxLevel    	Diameter    	MinVol      	VolCurve' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Pipes [PIPES] =================================================================
class sectionPipes(sectionAbstract):
    def __init__(self, inpM):
        super(sectionPipes, self).__init__(inpM, 5)
        self.name = '[PIPES]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';ID              	Node1           	Node2           	Length      	Diameter    	Roughness   	MinorLoss   	Status' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Pumps [PUMPS] =================================================================
class sectionPumps(sectionAbstract):
    def __init__(self, inpM):
        super(sectionPumps, self).__init__(inpM, 6)
        self.name = '[PUMPS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';ID              	Node1           	Node2           	Parameters' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Valves [VALVES] =================================================================
class sectionValves(sectionAbstract):
    def __init__(self, inpM):
        super(sectionValves, self).__init__(inpM, 7)
        self.name = '[VALVES]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';ID              	Node1           	Node2           	Diameter    	Type	Setting     	MinorLoss   ' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Tags [TAGS] =================================================================
class sectionTags(sectionAbstract):
    def __init__(self, inpM):
        super(sectionTags, self).__init__(inpM, 8)
        self.name = '[TAGS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Demands [DEMANDS] =================================================================
class sectionDemands(sectionAbstract):
    def __init__(self, inpM):
        super(sectionDemands, self).__init__(inpM, 9)
        self.name = '[DEMANDS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';Junction        	Demand      	Pattern         	Category ' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Status [STATUS] =================================================================
class sectionStatus(sectionAbstract):
    def __init__(self, inpM):
        super(sectionStatus, self).__init__(inpM, 10)
        self.name = '[STATUS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';ID              	Status/Setting' + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Patterns [PATTERNS] =================================================================
class sectionPatterns(sectionAbstract):
    def __init__(self, inpM):
        super(sectionPatterns, self).__init__(inpM, 11)
        self.name = '[PATTERNS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';ID              	Multipliers' + '\n')
        text = ";General Default Demand Pattern\n"
        text += "1               	1.34        	1.94        	1.46        	1.44        	0.76         	0.92"
        text += "1               	0.85         	1.07        	0.96         	1.1         	1.08        	1.19"
        text += "1               	1.16        	1.08        	0.96         	0.83         	0.79         	0.74"
        text += "1               	0.64         	0.64         	0.85         	0.96         	1.24        	1.67"
        outfile.write(text + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Curves [CURVES] =================================================================
class sectionCurves(sectionAbstract):
    def __init__(self, inpM):
        super(sectionCurves, self).__init__(inpM, 12)
        self.name = '[CURVES]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';ID              	X-Value     	Y-Value' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Controls [CONTROLS] =================================================================
class sectionControls(sectionAbstract):
    def __init__(self, inpM):
        super(sectionControls, self).__init__(inpM, 13)
        self.name = '[CONTROLS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Rules [RULES] =================================================================
class sectionRules(sectionAbstract):
    def __init__(self, inpM):
        super(sectionRules, self).__init__(inpM, 14)
        self.name = '[RULES]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Energy [ENERGY] =================================================================
class sectionEnergy(sectionAbstract):
    def __init__(self, inpM):
        super(sectionEnergy, self).__init__(inpM, 15)
        self.name = '[ENERGY]'
        
    def writeSection(self, outfile):
        result = self.INPManager.options[INP_Options.Energy]
        outfile.write(str(result))
        outfile.write('\n')

# Section Emitters [EMITTERS] =================================================================
class sectionEmitters(sectionAbstract):
    def __init__(self, inpM):
        super(sectionEmitters, self).__init__(inpM, 16)
        self.name = '[EMITTERS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';Junction        	Coefficient' + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Quality [QUALITY] =================================================================
class sectionQuality(sectionAbstract):
    def __init__(self, inpM):
        super(sectionQuality, self).__init__(inpM, 17)
        self.name = '[QUALITY]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';Node            	InitQual' + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Sources [SOURCES] =================================================================
class sectionSources(sectionAbstract):
    def __init__(self, inpM):
        super(sectionSources, self).__init__(inpM, 18)
        self.name = '[SOURCES]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';Node            	InitQual' + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Reactions [REACTIONS] =================================================================
class sectionReactions(sectionAbstract):
    def __init__(self, inpM):
        super(sectionReactions, self).__init__(inpM, 19)
        self.name = '[REACTIONS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';Type     	Pipe/Tank       	Coefficient' + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Reactions20 [REACTIONS] =================================================================
class sectionReactions20(sectionAbstract):
    def __init__(self, inpM):
        super(sectionReactions20, self).__init__(inpM, 20)
        self.name = '[REACTIONS]'
        
    def writeSection(self, outfile):
        # outfile.write(self.name + '\n')
        # outfile.write(' Order Bulk            	1' + '\n')
        # outfile.write(' Order Tank            	1' + '\n')
        # outfile.write(' Order Wall            	1' + '\n')
        # outfile.write(' Global Bulk           	0' + '\n')
        # outfile.write(' Global Wall           	0' + '\n')
        # outfile.write(' Limiting Potential    	0' + '\n')
        # outfile.write(' Roughness Correlation 	0' + '\n')
        result = self.INPManager.options[INP_Options.Reactions]
        outfile.write(str(result))
        outfile.write('\n')

# Section Mixing [MIXING] =================================================================
class sectionMixing(sectionAbstract):
    def __init__(self, inpM):
        super(sectionMixing, self).__init__(inpM, 21)
        self.name = '[MIXING]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';Tank            	Model' + '\n')
        #imprimir el otro contenido de la section
        outfile.write('\n')

# Section Times [TIMES] =================================================================
class sectionTimes(sectionAbstract):
    def __init__(self, inpM):
        super(sectionTimes, self).__init__(inpM, 22)
        self.name = '[TIMES]'
        
    def writeSection(self, outfile):
        result = self.INPManager.options[INP_Options.Times]
        outfile.write(str(result))
        outfile.write('\n')


# Section Report [REPORT] =================================================================
class sectionReport(sectionAbstract):
    def __init__(self, inpM):
        super(sectionReport, self).__init__(inpM, 23)
        self.name = '[REPORT]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(' Status             	No' + '\n')
        outfile.write(' Summary            	No' + '\n')
        outfile.write(' Page               	0' + '\n')
        outfile.write('\n')

# Section Options [OPTIONS] =================================================================
class sectionOptions(sectionAbstract):
    def __init__(self, inpM):
        super(sectionOptions, self).__init__(inpM, 24)
        self.name = '[OPTIONS]'
        # self._options = None
        
    # def setOptions(self, options: WateringINPOptions):
    #     self._options = options
        
    def writeSection(self, outfile):
        result = self.INPManager.options[INP_Options.Hydraulics]
        outfile.write(str(result))
        outfile.write('\n')

# Section Coordinates [COORDINATES] =================================================================
class sectionCoordinates(sectionAbstract):
    def __init__(self, inpM):
        super(sectionCoordinates, self).__init__(inpM, 25)
        self.name = '[COORDINATES]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';Node            	X-Coord         	Y-Coord' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Vertices [VERTICES] =================================================================
class sectionVertices(sectionAbstract):
    def __init__(self, inpM):
        super(sectionVertices, self).__init__(inpM, 26)
        self.name = '[VERTICES]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';Link            	X-Coord         	Y-Coord' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Labels [LABELS] =================================================================
class sectionLabels(sectionAbstract):
    def __init__(self, inpM):
        super(sectionLabels, self).__init__(inpM, 27)
        self.name = '[LABELS]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        outfile.write(';X-Coord            Y-Coord         Label & Anchor Node' + '\n')
        
        for item in self.values:
            outfile.write(f"{item!s}\n")
        
        outfile.write('\n')

# Section Backdrop [BACKDROP] =================================================================
class sectionBackdrop(sectionAbstract):
    def __init__(self, inpM):
        super(sectionBackdrop, self).__init__(inpM, 28)
        self.name = '[BACKDROP]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')
        # outfile.write(' DIMENSIONS     	0.00            	0.00            	10000.00        	10000.00        ' + '\n')
        # outfile.write(' UNITS          	Ninguno' + '\n')
        # outfile.write(' FILE           	' + '\n')
        # outfile.write(' OFFSET         	0.00            	0.00            ' + '\n')
        outfile.write('\n')

# Section End [END] =================================================================
class sectionEnd(sectionAbstract):
    def __init__(self, inpM):
        super(sectionEnd, self).__init__(inpM, 29)
        self.name = '[END]'
        
    def writeSection(self, outfile):
        outfile.write(self.name + '\n')