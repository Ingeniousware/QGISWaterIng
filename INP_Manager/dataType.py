# -*- coding: utf-8 -*-

"""
***************************************************************************
    dataType.py
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

from abc import ABC, abstractmethod
import warnings

from .inp_options_enum import INP_Options

# from __future__ import annotations

class AbstractOption(ABC):
    def __init__(self, inpM):
        # from .INPManager import INPManager
        super(AbstractOption, self).__init__()
        self._properties =  {}
        # Diccionario de descripciones
        self._descriptions = {}
        self._inpManeger = inpM

    def add_from_dict(self, dict: dict):
        for key, value in dict.items():
            self.add(key, value)

    def get(self, key):
        return self._properties.get(key, None)

    def keys(self):
        self._properties.keys()

    def values(self):
        self._properties.values()

    def update(self, key, valor):
        self._properties[key] = valor

    def len(self):
        return len(self._properties)

    # def exists(self, clave):
    #     return clave in self._properties


    @abstractmethod
    def read_properties(self, fileName: str):
        pass


    @abstractmethod
    def write_properties(self, fileName: str):
        pass


class Junction():
    #ID              	Elev        	Demand      	Pattern
    def __init__(self, id = "", elev = 0.0, demand = 0.0, pattern = "", description = ""):
        self.ID = id if id  else ""
        self.Elev = elev if elev else 0.0
        self.Demand = demand if demand else 0.0
        self.Pattern = pattern if pattern else ""
        self.Description = description if description else ""
    
    def __str__(self):
        return f" {self.ID: <15}\t{self.Elev: <12}\t{self.Demand: <12}\t{self.Pattern: <15};{self.Description}"

class Reservoir():
    #ID              	Head        	Pattern
    def __init__(self, id = "", head = 0.0, pattern = "", description = ""):
        self.ID = id if id  else ""
        self.Head = head if head else 0.0
        self.Pattern = pattern if pattern else ""
        self.Description = description if description else ""
    
    def __str__(self):
        return f" {self.ID: <15}\t{self.Head: <12}\t{self.Pattern: <15};{self.Description}"

class Tank():
    #ID              	Elevation   	InitLevel   	MinLevel    	MaxLevel    	Diameter    	MinVol      	VolCurve
    def __init__(self, id = "", elevation = 0.0, initLevel = 0.0, minLevel = 0.0, maxLevel = 0.0, diameter = 0.0, minVol = 0.0, volCurve = None, description = ""):
        self.ID = id if id else ""
        self.Elevation = elevation if elevation else 0.0
        self.InitLevel = initLevel if initLevel else 0.0
        self.MinLevel = minLevel if minLevel else 0.0
        self.MaxLevel = maxLevel if maxLevel else 0.0
        self.Diameter = diameter if diameter else 0.0
        self.MinVol = minVol if minVol else 0.0
        self.VolCurve = volCurve if volCurve is not None else ""
        self.Description = description if description else ""
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Elevation: <12}\t{self.InitLevel: <12}\t{self.MinLevel: <12}\t{self.MaxLevel: <12}\t{self.Diameter: <12}\t{self.MinVol: <12}\t{self.VolCurve: <15};{self.Description}"

class Pipe():
    #ID              	Node1           	Node2           	Length      	Diameter    	Roughness   	MinorLoss   	Status
    def __init__(self, id = "", node1 = "", node2 = "", length = 0.0, diameter = 0.0, roughness = 0.0, minorLoss = 0.0, status = "", description = ""):
        self.ID = id if id else ""
        self.Node1 = node1 if node1 else ""
        self.Node2 = node2 if node2 else ""
        self.Length = length if length else 0.0
        self.Diameter = diameter if diameter else 0.0
        self.Roughness = roughness if roughness else 0.0
        self.MinorLoss = minorLoss if minorLoss else 0.0
        self.Status = status if status else ""
        self.Description = description if description else ""
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Node1: <17}\t{self.Node2: <17}\t{self.Length: <12.4f}\t{self.Diameter: <12}\t{self.Roughness: <12}\t{self.MinorLoss: <12}\t{self.Status: <15};{self.Description}"
    
class Pump():
    #ID              	Node1           	Node2           	Parameters
    def __init__(self, id = "", node1 = 0, node2 = 0, pattern = "", description = ""):
        self.ID = id if id else ""
        self.Node1 = node1 if node1 else ""
        self.Node2 = node2 if node2 else ""
        self.Pattern = pattern if pattern else ""
        self.Description = description if description else ""
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Node1: <17}\t{self.Node2: <17}\t{self.Pattern: <15};{self.Description}"

class Valve():
    #ID              	Node1           	Node2           	Diameter    	Type	Setting     	MinorLoss
    def __init__(self, id = "", node1 = 0.0, node2 = 0.0, diameter = 0.0, type = "", setting = "", minorLoss = 0.0, description = ""):
        self.ID = id if id else ""
        self.Node1 = node1 if node1 else ""
        self.Node2 = node2 if node2 else ""
        self.Diameter = diameter if diameter else 0.0
        self.Type = type if type else ""
        self.Setting = setting if setting else ""
        self.MinorLoss = minorLoss if minorLoss else 0.0
        self.Description = description if description else ""
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Node1: <17}\t{self.Node2: <17}\t{self.Diameter: <12}\t{self.Type: <4}\t{self.Setting: <12}\t{self.MinorLoss: <15};{self.Description}"
    
class Tag():
    #Ejemplo de Tag NODE 	4               	Nodo_Terminal
    #Para nodo, tanques embales el type es NODE y para tuberias, bombas y valvulas el type es LINK
    def __init__(self, typeNode = "NODE", id = "", label = ""):
        self.Type = typeNode if typeNode else "NODE"
        self.ID = id if id else ""
        self.Label = label if label else ""
    
    def __str__(self):
        return f" {self.Type: <6}\t{self.ID: <16}\t{self.Label}"
    
class Demand():
    #Junction        	Demand      	Pattern         	Category
    def __init__(self, junction = "", demand = 0.0, pattern = "", category = ""):
        self.Junction = junction if junction else ""
        self.Demand = demand if demand else 0.0
        self.Pattern = pattern if pattern else ""
        self.Category = category if category else ""
    
    def __str__(self):
        return f" {self.Junction: <15}\t{self.Demand: <12}\t{self.Pattern: <17}\t{self.Category: <15};"
    
class Pattern():
    #ID              	Multipliers
    def __init__(self, description = "", id = "", multiplers = []):
        self.Description = description if description else ""
        self.ID = id if id else ""
        self.Multipliers = multiplers
    def __str__(self):
        text = f";{self.Description}\n {self.ID: <16}\t"
        i = 0
        for item in self.Multipliers:
            if (i < 5):
                text += f"{item: <12}\t"
            elif (i == 5):
                text += f"{item: <12}\n"
            else:
                i = -1
                text += f" {self.ID: <16}\t"
            i += 1
        return text
    
class Curve():
    #ID              	X-Value     	Y-Value
    def __init__(self, id = "", x_value = 0.0, y_value = 0.0):
        self.ID = id if id else ""
        self.X_value = x_value if x_value else 0.0
        self.Y_value = y_value if y_value else 0.0
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.X_value: <12}\t{self.Y_value: <15};"
    
######################### Proximas class #####################################################
class Time_Options(AbstractOption):
    """
    Options related to simulation and model timing.
    These options are named according to the EPANET 2.2 "Times" settings.
    
    Parameters
    ----------
    duration : int
        Simulation duration (seconds), by default 0.

    hydraulic_timestep : int >= 1
        Hydraulic timestep (seconds), by default 3600 (one hour).

    quality_timestep : int >= 1
        Water quality timestep (seconds), by default 360 (five minutes).

    rule_timestep : int >= 1
        Rule timestep (seconds), by default 360 (five minutes).

    pattern_timestep : int >= 1
        Pattern timestep (seconds), by default 3600 (one hour).

    pattern_start : int
        Time offset (in seconds) to find the starting pattern step; changes
        where in pattern the pattern starts out, *not* what time the pattern
        starts, by default 0.

    report_timestep : int >= 1
        Reporting timestep (seconds), by default 3600 (one hour).

    report_start : int
        Start time of the report (in seconds) from the start of the simulation, by default 0.

    start_clocktime : int
        Time of day (in seconds from midnight) at which the simulation begins, by default 0 (midnight).

    statistic: str
        Provide statistics rather than time series report in the report file.
        Options are "AVERAGED", "MINIMUM", "MAXIUM", "RANGE", and "NONE" (as defined in the
        EPANET User Manual). Defaults to "NONE".

    pattern_interpolation: bool
        **Only used by the WNTRSimulator**. Defaults to False. If True, interpolation will
        be used determine pattern values between pattern timesteps. If
        False, patterns cause step-like behavior where the pattern
        value corresponding to the most recent pattern timestep is
        used until the next pattern timestep. For example, given the
        pattern [1, 1.2, 1.6], a pattern timestep of 1 hour, and a
        pattern_interpolation value of False, a value of 1 is used at
        0 hours and every time strictly less than 1 hour. A value of
        1.2 is used at hour 1 and every time strictly less than 2
        hours. With a pattern_interpolation value of True, a value of
        1 is used at 0 hours and a value of 1.2 is used at 1
        hour. However, at an intermediat time such as 0.5 hours,
        interpolation is used, resulting in a value of 1.1. Using
        interpolation with a shorter hydraulic_timestep can make
        problems with large changes in patterns (e.g., large changes
        in demand) easier to solve.

    """
    
    def __init__(self, inpM,
                duration: str = "00:00",
                hydraulic_timestep: str = "01:00",
                quality_timestep: str = "00:05",
                pattern_timestep: str = "01:00",
                pattern_start: str = "00:00",
                report_timestep: str = "01:00",
                report_start: str = "00:00",
                start_clocktime: str = "12 am",
                statistic: str='NONE'):
        super().__init__(inpM)
        self.duration = duration
        self.hydraulic_timestep = hydraulic_timestep
        self.quality_timestep = quality_timestep
        self.pattern_timestep = pattern_timestep
        self.pattern_start = pattern_start
        self.report_timestep = report_timestep
        self.report_start = report_start
        self.start_clocktime = start_clocktime
        self.statistic = statistic
        self._properties = {"statistic": ['AVERAGED', 'MINIMUM', 'MAXIMUM', 'RANGE', 'NONE'],
                            "pattern_interpolation": [False, True]}
        self._descriptions = {'duration': 'Duration',
                              'hydraulic_timestep': 'Hydraulic Timestep',
                              'quality_timestep': 'Quality Timestep',
                              'pattern_timestep': 'Pattern Timestep',
                              'pattern_start': 'Pattern Start',
                              'report_timestep': 'Report Timestep',
                              'report_start': 'Report Start',
                              'start_clocktime': 'Start ClockTime',
                              'statistic': 'Statistic'}


    def read_properties(self, fileName):
        return super().read_properties(fileName)


    def write_properties(self, fileName):
        return super().write_properties(fileName)


    def __str__(self):
        text = "[TIMES]\n"
        text += f" Duration           	{self.duration}\n Hydraulic Timestep 	{self.hydraulic_timestep}\n Quality Timestep   	{self.quality_timestep}\n"
        text += f" Pattern Timestep   	{self.pattern_timestep}\n Pattern Start      	{self.pattern_start}\n Report Timestep    	{self.report_timestep}\n"
        text += f" Report Start       	{self.report_start}\n Start ClockTime    	{self.start_clocktime}\n Statistic          	{self.statistic}\n"
        return text


class Hydraulic_Options(AbstractOption):
    """
    Options related to hydraulic model.
    These options are named according to the settings in the EPANET "[OPTIONS]"
    section. Unless specified, these options are valid for both EPANET 2.0 and 2.2.

    Parameters
    ----------
    headloss : str
        Formula to use for computing head loss through a pipe. Options are "H-W",
        "D-W", and "C-M", by default "H-W".

    hydraulics : str
        Indicates if a hydraulics file should be read in or saved; options are
        ``None``, "USE" and "SAVE", by default ``None``.

    hydraulics_filename : str
        Filename to use if ``hydraulics is not None``, by default ``None``.

    viscosity : float
        Kinematic viscosity of the fluid, by default 1.0.

    specific_gravity : float
        Specific gravity of the fluid, by default 1.0.

    pattern : str
        Name of the default pattern for junction demands. By default,
        the default pattern is the pattern named "1". If this is set
        to None (or if pattern "1" does not exist), then
        junctions with demands but without patterns will be held constant.

    demand_multiplier : float
        The demand multiplier adjusts the values of baseline demands for all
        junctions, by default 1.0.

    emitter_exponent : float
        The exponent used when computing flow from an emitter, by default 0.5.

    minimum_pressure : float
        (EPANET 2.2 only) The global minimum nodal pressure, by default 0.0.

    required_pressure: float
        (EPANET 2.2 only) The required nodal pressure, by default 0.07 (m H2O)

    pressure_exponent: float
        (EPANET 2.2 only) The pressure exponent, by default 0.5.

    trials : int
        Maximum number of trials used to solve network hydraulics, by default 200.

    accuracy : float
        Convergence criteria for hydraulic solutions, by default 0.001.

    headerror : float
        (EPANET 2.2 only) Augments the `accuracy` option by adjusting the head
        error convergence limit, by default 0 (off).

    flowchange : float
        (EPANET 2.2 only) Augments the `accuracy` option by adjusting the flow
        change convergence limit, by default 0 (off).

    unbalanced : str
        Indicate what happens if a hydraulic solution cannot be reached.
        Options are "STOP" and "CONTINUE", by default "STOP".

    unbalanced_value : int
        Number of additional trials if ``unbalanced == "CONTINUE"``, by default ``None``.

    checkfreq : int
        Number of solution trials that pass between status checks, by default 2.

    maxcheck : int
        Number of solution trials that pass between status check, by default 10.

    damplimit : float
        Accuracy value at which solution damping begins, by default 0 (no damping).

    demand_model : str
        Demand model for EPANET 2.2; acceptable values are "DD" and "PDD", by default "DD".
        EPANET 2.0 only contains demand driven analysis, and will issue a warning
        if this option is not set to DD.

    inpfile_units : str
        Units for the INP file; options are "CFS", "GPM", "MGD", "IMGD", "AFD", "LPS",
        "LPM", "MLD", "CMH", and "CMD". This **only** changes the units used in generating
        the INP file -- it has **no impact** on the units used in WNTR, which are
        **always** SI units (m, kg, s).

    inpfile_pressure_units: str
        Pressure units for the INP file, by default None (uses pressure units from inpfile_units)

    """
    def __init__(self, inpM,
                 headloss: str = 'H-W',
                 hydraulics: str = None,
                 viscosity: float = 1.0,
                 specific_gravity: float = 1.0,
                 pattern: str = '1',
                 demand_multiplier: float = 1.0,
                 demand_model: str = 'DDA',
                 minimum_pressure: float = 0.0,
                 required_pressure: float = 0.1,  # EPANET 2.2 default
                 pressure_exponent: float = 0.5,
                 emitter_exponent: float = 0.5,
                 trials: int = 40,  # EPANET 2.2 increased the default from 40 to 200
                 accuracy: float = 0.001,
                 unbalanced: str = 'Continue 10',
                 unbalanced_value: int = None,
                 checkfreq: int = 2,
                 maxcheck: int = 10,
                 damplimit: int = 0,
                 headerror: float = 0,
                 flowchange: float = 0,
                 inpfile_units: str = 'LPS',
                 inpfile_pressure_units: str = None):
        super().__init__(inpM)
        self.headloss = headloss
        self.hydraulics = hydraulics
        self.viscosity = viscosity
        self.specific_gravity = specific_gravity
        self.pattern = pattern
        self.demand_multiplier = demand_multiplier
        self.demand_model = demand_model
        self.minimum_pressure = minimum_pressure
        self.required_pressure = required_pressure
        self.pressure_exponent = pressure_exponent
        self.emitter_exponent = emitter_exponent
        self.trials = trials
        self.accuracy = accuracy
        self.unbalanced = unbalanced
        self.unbalanced_value = unbalanced_value
        self.checkfreq = checkfreq
        self.maxcheck = maxcheck
        self.damplimit = damplimit
        self.headerror = headerror
        self.flowchange = flowchange
        self.inpfile_units = inpfile_units
        self.inpfile_pressure_units = inpfile_pressure_units
        self._properties = {"inpfile_units": ['CFS', 'GPM', 'MGD', 'IMGD', 'AFD', 'LPS', 'LPM', 'MLD', 'CMH', 'CMD'],
                            "headloss": ['H-W', 'D-W', 'C-M'],
                            "demand_model": ['DDA', 'PDA'],
                            "hydraulics": ['None', 'USE', 'SAVE'],
                            "unbalanced": ['STOP', 'CONTINUE']}
        self._descriptions = {'inpfile_units': 'Units',
                              'headloss': 'Headloss',
                              'specific_gravity': 'Specific gravity',
                              'viscosity': 'Viscosity',
                              'trials': 'Trials',
                              'accuracy': 'Accuracy',
                              'checkfreq': 'CHECKFREQ',
                              'maxcheck': 'MAXCHECK',
                              'damplimit': 'damplimit',
                              'unbalanced': 'Unbalanced',
                              'pattern': 'Pattern',
                              'demand_multiplier': 'Demand Multiplier',
                              'demand_model': 'Demand Model',
                              'minimum_pressure': 'Minimum Pressure',
                              'required_pressure': 'Required Pressure',
                              'pressure_exponent': 'Pressure Exponent',
                              'emitter_exponent': 'Emitter Exponent',
                              'diffusivity': 'Diffusivity',
                              'tolerance': 'Tolerance'}


    def read_properties(self, fileName):
        return super().read_properties(fileName)


    def write_properties(self, fileName):
        return super().write_properties(fileName)


    def __str__(self):
        quality: Quality_Options = self._inpManeger.options[INP_Options.Quality] # if self._options is not None else QualityOptions()
        txt = quality.parameter + ' ' + quality.inpfile_units
        text = "[OPTIONS]\n"
        text += f" Units              	{self.inpfile_units}\n Headloss           	{self.headloss}\n Specific Gravity   	{self.specific_gravity}\n"
        text += f" Viscosity          	{self.viscosity}\n Trials             	{self.trials}\n Accuracy           	{self.accuracy}\n"
        text += f" CHECKFREQ          	{self.checkfreq}\n MAXCHECK           	{self.maxcheck}\n DAMPLIMIT          	{self.damplimit}\n"
        text += f" Unbalanced         	{self.unbalanced}\n Pattern            	{self.pattern}\n Demand Multiplier  	{self.demand_multiplier}\n"
        text += f" Demand Model       	{self.demand_model}\n Minimum Pressure   	{self.minimum_pressure}\n Required Pressure  	{self.required_pressure}\n"
        text += f" Pressure Exponent  	{self.pressure_exponent}\n Emitter Exponent   	{self.emitter_exponent}\n Quality            	{txt}\n"
        text += f" Diffusivity        	{quality.diffusivity}\n Tolerance          	{quality.tolerance}\n"
        return text


class Reaction_Options(AbstractOption):
    """
    Options related to water quality reactions.
    From the EPANET "[REACTIONS]" options.
    
    Parameters
    ----------
    bulk_order : float
        Order of reaction occurring in the bulk fluid, by default 1.0.

    wall_order : float
        Order of reaction occurring at the pipe wall; must be either 0 or 1, by default 1.0.

    tank_order : float
        Order of reaction occurring in the tanks, by default 1.0.

    bulk_coeff : float
        Global reaction coefficient for bulk fluid and tanks, by default 0.0.

    wall_coeff : float
        Global reaction coefficient for pipe walls, by default 0.0.

    limiting_potential : float
        Specifies that reaction rates are proportional to the difference
        between the current concentration and some limiting potential value,
        by default ``None`` (off).

    roughness_correl : float
        Makes all default pipe wall reaction coefficients related to pipe
        roughness, according to functions as defined in EPANET, by default
        ``None`` (off).


    .. note::

        Remember to use positive numbers for growth reaction coefficients and
        negative numbers for decay coefficients. The time units for all reaction
        coefficients are in "per-second" and converted to/from EPANET units during I/O.

    """
    def __init__(self, inpM,
                 bulk_order: float = 1.0,
                 wall_order: float = 1.0,
                 tank_order: float = 1.0,
                 bulk_coeff: float = 0.0,
                 wall_coeff: float = 0.0,
                 limiting_potential: float = 0.0,
                 roughness_correl: float = 0.0):
        super().__init__(inpM)
        self.bulk_order = bulk_order
        self.wall_order = wall_order
        self.tank_order = tank_order
        self.bulk_coeff = bulk_coeff
        self.wall_coeff = wall_coeff
        self.limiting_potential = limiting_potential
        self.roughness_correl = roughness_correl


    def read_properties(self, fileName):
        return super().read_properties(fileName)


    def write_properties(self, fileName):
        return super().write_properties(fileName)


    def __str__(self):
        text = "[REACTIONS]\n"
        text += f" Order Bulk            	{self.bulk_order}\n Order Tank            	{self.tank_order}\n Order Wall            	{self.wall_order}\n"
        text += f" Global Bulk           	{self.bulk_coeff}\n Global Wall           	{self.wall_coeff}\n Limiting Potential    	{self.limiting_potential}\n"
        text += f" Roughness Correlation 	{self.roughness_correl}\n"
        return text


class Quality_Options(AbstractOption):
    """
    Options related to water quality modeling. These options come from
    the "[OPTIONS]" section of an EPANET INP file.

    Parameters
    ----------
    parameter : str
        Type of water quality analysis.  Options are "NONE", "CHEMICAL", "AGE", and
        "TRACE", by default ``None``.

    trace_node : str
        Trace node name if ``quality == "TRACE"``, by default ``None``.

    chemical : str
        Chemical name for "CHEMICAL" analysis, by default "CHEMICAL" if appropriate.

    diffusivity : float
        Molecular diffusivity of the chemical, by default 1.0.

    tolerance : float
        Water quality solver tolerance, by default 0.01.

    inpfile_units : str
        Units for quality analysis if the parameter is set to CHEMICAL.
        This is **only** relevant for the INP file. This value **must** be either
        "mg/L" (default) or "ug/L" (miligrams or micrograms per liter).
        Internal WNTR units are always SI units (kg/m3).


    """
    def __init__(self, inpM,
                 parameter: str = 'NONE',
                 trace_node: str = None,
                 chemical_name: str = 'CHEMICAL',
                 diffusivity: float = 1.0,
                 tolerance: float = 0.01,
                 inpfile_units: str = 'mg/L'):
        super().__init__(inpM)
        self.parameter = parameter
        self.trace_node = trace_node
        self.chemical_name = chemical_name
        self.diffusivity = diffusivity
        self.tolerance = tolerance
        self.inpfile_units = inpfile_units
        self._properties = {"parameter":['NONE', 'CHEMICAL', 'AGE', 'TRACE'],
                            "inpfile_units": ['mg/L', 'ug/L']}


    def read_properties(self, fileName):
        return super().read_properties(fileName)


    def write_properties(self, fileName):
        return super().write_properties(fileName)


    def __str__(self):
        text = "[QUALITY]\n"
        text += f" Parameter            	{self.parameter}\n Trace Node            	{self.trace_node}\n Chemical Name      	{self.chemical_name}\n"
        text += f" Diffusivity           	{self.diffusivity}\n Tolerance           	{self.tolerance}\n iINP file units    	{self.inpfile_units}\n"
        return text


class Energy_Options(AbstractOption):
    """
    Options related to energy calculations.
    From the EPANET "[ENERGY]" settings.

    Parameters
    ----------
    global_price : float
        Global average cost per Joule, by default 0.

    global_pattern : str
        ID label of time pattern describing how energy price varies with
        time, by default ``None``.

    global_efficiency : float
        Global pump efficiency as percent; i.e., 75.0 means 75%,
        by default ``None``.

    demand_charge : float
        Added cost per maximum kW usage during the simulation period,
        by default ``None``.
    """
    def __init__(self, inpM,
                global_price: float = 0.0,
                global_pattern: str = None,
                global_efficiency: float = 75,
                demand_charge: float = 0.0):
        super().__init__(inpM)
        self.global_price = global_price
        self.global_pattern = global_pattern
        self.global_efficiency = global_efficiency
        self.demand_charge = demand_charge


    def read_properties(self, fileName):
        return super().read_properties(fileName)


    def write_properties(self, fileName):
        return super().write_properties(fileName)


    def __str__(self):
        text = "[ENERGY]\n"
        text += f" Global Efficiency  	{self.global_efficiency}\n Global Price       	{self.global_price}\n"
        text += f" Demand Charge      	{self.demand_charge}\n"
        return text

######################### Proximas class #####################################################
class Coordinate():
    #Node            	X-Coord         	Y-Coord
    def __init__(self, node = "", x_coord = 0.0, y_coord = 0.0):
        self.Node = node if node else ""
        self.X_Coord = x_coord if x_coord else 0.0
        self.Y_Coord = y_coord if y_coord else 0.0
    
    def __str__(self):
        return f" {self.Node: <15}\t{self.X_Coord: <16}\t{self.Y_Coord: <15};"
    
class Vertice():
    #Link            	X-Coord         	Y-Coord
    def __init__(self, link = "", x_coord = 0.0, y_coord = 0.0):
        self.Link = link if link else ""
        self.X_Coord = x_coord if x_coord else 0.0
        self.Y_Coord = y_coord if y_coord else 0.0
        
    def __str__(self):
        return f" {self.Link: <15}\t{self.X_Coord: <16}\t{self.Y_Coord: <15};"
    
class Label():
    #X-Coord           Y-Coord          Label & Anchor Node
    def __init__(self, x_coord = 0.0, y_coord = 0.0, anchor_node = ""):
        self.X_Coord = x_coord if x_coord else 0.0
        self.Y_Coord = y_coord if y_coord else 0.0
        self.Anchor_node = anchor_node if anchor_node else ""
        
    def __str__(self):
        return f" {self.X_Coord: <15}\t{self.Y_Coord: <12}\t{self.Anchor_node: <15};"
    
class Backdrop():
    def __init__(self, xmin = 0.0, ymin = 0.0, xmax = 10000.0, ymax = 10000.0, units = "NONE", file = "", offsetx = 0.0, offsety = 0.0):
        self.x_min = xmin if xmin else 0.0
        self.y_min = ymin if ymin else 0
        self.x_max = xmax if xmax else 0.0
        self.y_max = ymax if ymax else 0.0
        self.Units = units if units else "NONE"
        self.File = file if file else ""
        self.offset_x = offsetx if offsetx else 0.0
        self.offset_y = offsety if offsety else 0.0
        
    def __str__(self):
        return f" DIMENSIONS     	{self.x_min: <17}\t{self.y_min: <17}\t{self.x_max: <17}\t{self.y_max: <17}\n UNITS          	{self.Units}\n FILE           	{self.File}\n OFFSET         	{self.offset_x: <17}\t{self.offset_y: <17}"
################################################################ Proximas class