# -*- coding: utf-8 -*-

"""
***************************************************************************
    INPManager.py
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

from .sections import sectionTitle, sectionJunctions, sectionReservoirs, sectionTanks, sectionPipes, sectionPumps, sectionValves, sectionTags, sectionDemands, sectionStatus, sectionPatterns, sectionCurves, sectionControls, sectionRules, sectionEnergy, sectionEmitters, sectionQuality, sectionSources, sectionReactions, sectionReactions20, sectionMixing, sectionTimes, sectionReport, sectionOptions, sectionCoordinates, sectionVertices, sectionLabels, sectionBackdrop, sectionEnd
from .dataType import Junction, Reservoir, Tank, Pipe, Pump, Valve, Demand, Curve, Coordinate, Vertice, Label

class INPManager():
    def __init__(self, outfile=None):
        self.outfile = outfile

        self.sections = {'TITLE': sectionTitle('PRUEBA DE INP'),# - 1 - Ok
                         'JUNCTIONS': sectionJunctions(),# - 1 - Ok
                         'RESERVOIRS': sectionReservoirs(),# - 1- Ok
                         'TANKS': sectionTanks(),# - 1 - Ok
                         'PIPES': sectionPipes(),# - 1 - Ok
                         'PUMPS': sectionPumps(),# - 1 - Ok
                         'VALVES': sectionValves(),# - 1 - Ok
                         'TAGS': sectionTags(),
                         'DEMANDS': sectionDemands(),# - 1 - Ok
                         'STATUS': sectionStatus(),
                         'PATTERNS': sectionPatterns(),
                         'CURVES': sectionCurves(),# - 1 - Ok
                         'CONTROLS': sectionControls(),
                         'RULES': sectionRules(),
                         'ENERGY': sectionEnergy(),
                         'EMITTERS': sectionEmitters(),
                         'QUALITY': sectionQuality(),
                         'SOURCES': sectionSources(),
                         'REACTIONS': sectionReactions(),
                         'REACTIONS20': sectionReactions20(),
                         'MIXING': sectionMixing(),
                         'TIMES': sectionTimes(),
                         'REPORT': sectionReport(),
                         'OPTIONS': sectionOptions(), # - 1 - Ok
                         'COORDINATES': sectionCoordinates(),# - 1 - Ok
                         'VERTICES': sectionVertices(),# - 1 - Ok
                         'LABELS': sectionLabels(),# - 1 - Ok
                         'BACKDROP': sectionBackdrop(),
                         'END': sectionEnd()}
        #Testing para las sections.
        junctions = self.sections['JUNCTIONS']
        for i in range(1, 5):
            junctions.values.append(Junction(i, (i + 1 * 2), (i * 2 + 1), (i * 3 + 1)))
        
        reservoirs = self.sections['RESERVOIRS']
        for i in range(1, 5):
            reservoirs.values.append(Reservoir(i, (i + 1 * 2), (i * 3 + 1)))
        
        tank = self.sections['TANKS']
        for i in range(1, 5):
            tank.values.append(Tank(i, (i + 1 * 2), (i * 2 + 1), (i * 3 + 1), (i * 2 + 3), (i * 4 + 4), (i * 5 + 1), (i * 2 + 5)))
        
        pipe = self.sections['PIPES']
        for i in range(1, 5):
            pipe.values.append(Pipe(i, (i + 1 * 2), (i * 2 + 1), (i * 3 + 1), (i * 2 + 3), (i * 4 + 4), (i * 5 + 1), (i * 2 + 5)))
        
        pump = self.sections['PUMPS']
        for i in range(1, 5):
            pump.values.append(Pump(i, (i + 1 * 2), (i * 2 + 1), (i * 3 + 1)))
        
        valve = self.sections['VALVES']
        for i in range(1, 5):
            valve.values.append(Valve(i, (i + 1 * 2), (i * 2 + 1), (i * 3 + 1), (i * 2 + 3), (i * 4 + 4), (i * 5 + 1)))
        
        demand = self.sections['DEMANDS']
        for i in range(1, 5):
            demand.values.append(Demand(i, (i + 1 * 2), (i * 2 + 1), (i * 3 + 1)))
        
        curve = self.sections['CURVES']
        for i in range(1, 5):
            curve.values.append(Curve(i, (i + 1 * 2), (i * 2 + 1)))
        
        coordinate = self.sections['COORDINATES']
        for i in range(1, 5):
            coordinate.values.append(Coordinate(i, (i + 1 * 2), (i * 2 + 1)))
        
        vertice = self.sections['VERTICES']
        for i in range(1, 5):
            vertice.values.append(Vertice(i, (i + 1 * 2), (i * 2 + 1)))
        
        label = self.sections['LABELS']
        for i in range(1, 5):
            label.values.append(Label(i, (i + 1 * 2), (i * 2 + 1)))

    def writeSections(self, outfile=None):
        if outfile is not None:
            self.outfile = outfile

        #Se debe organizar los sections antes de mandarlas a escribir, comprobar que todas las secciones esten escritas de no estar escrita se crea vacia.

        for t, s in self.sections.items():
            print(t,s.name)
            s.writeSection(self.outfile)
