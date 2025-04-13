
import logging
import os
import sys
import warnings

import numpy as np
import pandas as pd

from .results import ResultsStatus, SimulationResults
from .util import EN, FlowUnits, HydParam, MassUnits, PressureUnits, QualParam, QualType, ResultType, StatisticsType, to_si


logger = logging.getLogger(__name__)
sys_default_enc = sys.getdefaultencoding()

class BinFile:
    """EPANET binary output file reader.
    
    This class provides read functionality for EPANET binary output files.
    
    Parameters
    ----------
    results_type : list of ResultType, optional
        This parameter is *only* active when using a subclass of the BinFile that implements
        a custom reader or writer, by default None. If None, then all results will be saved (node quality, 
        demand, link flow, etc.). Otherwise, a list of result types can be passed to limit the memory used.
    network : bool, optional
        Save a new WaterNetworkModel from the description in the output binary file, by default None. Certain
        elements may be missing, such as patterns and curves, if this is done.
    energy : bool, optional
        Save the pump energy results, by default False.
    statistics : bool, optional
        Save the statistics lines (different from the stats flag in the inp file) that are
        automatically calculated regarding hydraulic conditions, by default False.
    convert_status : bool, optional
        Convert the EPANET link status (8 values) to simpler WNTR status (3 values), by default True. 
        When this is done, the encoded-cause status values are converted simple stat
        values, instead.

    
    Returns
    -------
    SimulationResults
        A WNTR results object will be created and added to the instance after read.

    """
    def __init__(self, result_types=None, network=False, energy=False, statistics=False,
                 convert_status=True):
        if os.name in ['nt', 'dos'] or sys.platform in ['darwin']:
            self.ftype = '=f4'
        else:
            self.ftype = '=f4'
        self.idlen = 32
        self.convert_status = convert_status
        self.hydraulic_id = None
        self.quality_id = None
        self.node_names = None
        self.link_names = None
        self.report_times = None
        self.flow_units = None
        self.pres_units = None
        self.mass_units = None
        self.quality_type = None
        self.num_nodes = None
        self.num_tanks = None
        self.num_links = None
        self.num_pumps = None
        self.num_valves = None
        self.report_start = None
        self.report_step = None
        self.duration = None
        self.chemical = None
        self.chem_units = None
        self.inp_file = None
        self.report_file = None
        self.results = SimulationResults()
        if result_types is None:
            self.items = [ member for name, member in ResultType.__members__.items() ]
        else:
            self.items = result_types
        self.create_network = network
        self.keep_energy = energy
        self.keep_statistics = statistics

    def _get_time(self, t):
        s = int(t)
        h = int(s/3600)
        s -= h*3600
        m = int(s/60)
        s -= m*60
        s = int(s)
        return '{:02}:{:02}:{:02}'.format(h, m, s)

    def save_network_desc_line(self, element, values):
        """Save network description meta-data and element characteristics.

        This method, by default, does nothing. It is available to be overloaded, but the
        core implementation assumes that an INP file exists that will have a better,
        human readable network description.

        Parameters
        ----------
        element : str
            The information being saved
        values : numpy.array
            The values that go with the information

        """
        pass

    def save_energy_line(self, pump_idx, pump_name, values):
        """Save pump energy from the output file.

        This method, by default, does nothing. It is available to be overloaded
        in order to save information for pump energy calculations.

        Parameters
        ----------
        pump_idx : int
            the pump index
        pump_name : str
            the pump name
        values : numpy.array
            the values to save
			
        """
        pass

    def finalize_save(self, good_read, sim_warnings):
        """Post-process data before writing results.
        
        This method, by default, does nothing. It is available to be overloaded 
        in order to post process data.
        
        Parameters
        ----------
        good_read : bool
            was the full file read correctly
        sim_warnings : int
            were there warnings issued during the simulation
			
        """
        pass

#    @run_lineprofile()
    def read(self, filename, convergence_error=False, darcy_weisbach=False, convert=True):
        """Read a binary file and create a results object.

        Parameters
        ----------
        filename : str
            An EPANET BIN output file
        convergence_error: bool (optional)
            If convergence_error is True, an error will be raised if the
            simulation does not converge. If convergence_error is False, partial results are returned,
            a warning will be issued, and results.error_code will be set to 0
            if the simulation does not converge.  Default = False.

        Returns
        -------
        object
            returns a WaterNetworkResults object
        """
        self.results = SimulationResults()
        
        logger.debug('Read binary EPANET data from %s',filename)
        dt_str = 'u1'  #.format(self.idlen)
        with open(filename, 'rb') as fin:
            ftype = self.ftype
            idlen = self.idlen
            logger.debug('... read prolog information ...')
            prolog = np.fromfile(fin, dtype=np.int32, count=15)
            self._prolog = prolog
            magic1 = prolog[0]
            version = prolog[1]
            nnodes = prolog[2]
            ntanks = prolog[3]
            nlinks = prolog[4]
            npumps = prolog[5]
            nvalve = prolog[6]
            wqopt = QualType(prolog[7])
            srctrace = prolog[8]
            flowunits = FlowUnits(prolog[9])
            presunits = PressureUnits(prolog[10])
            statsflag = StatisticsType(prolog[11])
            reportstart = prolog[12]
            reportstep = prolog[13]
            duration = prolog[14]
            logger.debug('EPANET/Toolkit version %d',version)
            logger.debug('Nodes: %d; Tanks/Resrv: %d Links: %d; Pumps: %d; Valves: %d',
                         nnodes, ntanks, nlinks, npumps, nvalve)
            logger.debug('WQ opt: %s; Trace Node: %s; Flow Units %s; Pressure Units %s',
                         wqopt, srctrace, flowunits, presunits)
            logger.debug('Statistics: %s; Report Start %d, step %d; Duration=%d sec',
                         statsflag, reportstart, reportstep, duration)

            # Ignore the title lines
            np.fromfile(fin, dtype=np.uint8, count=240)
            inpfile = np.fromfile(fin, dtype=np.uint8, count=260)
            rptfile = np.fromfile(fin, dtype=np.uint8, count=260)
            chemical = bytes(np.fromfile(fin, dtype=dt_str, count=self.idlen)[:]).decode(sys_default_enc)
#            wqunits = ''.join([chr(f) for f in np.fromfile(fin, dtype=np.uint8, count=idlen) if f!=0 ])
            wqunits = bytes(np.fromfile(fin, dtype=dt_str, count=self.idlen)[:]).decode(sys_default_enc)
            mass = wqunits.split('/',1)[0]
            if mass in ['mg', 'ug', u'mg', u'ug']:
                massunits = MassUnits[mass]
            else:
                massunits = MassUnits.mg
            self.flow_units = flowunits
            self.pres_units = presunits
            self.quality_type = wqopt
            self.mass_units = massunits
            self.num_nodes = nnodes
            self.num_tanks = ntanks
            self.num_links = nlinks
            self.num_pumps = npumps
            self.num_valves = nvalve
            self.report_start = reportstart
            self.report_step = reportstep
            self.duration = duration
            self.chemical = chemical
            self.chem_units = wqunits
            self.inp_file = inpfile
            self.report_file = rptfile
            nodenames = []
            linknames = []
            nodenames = [bytes(np.fromfile(fin, dtype=dt_str, count=self.idlen)).decode(sys_default_enc).replace('\x00','') for _ in range(nnodes)] 
            linknames = [bytes(np.fromfile(fin, dtype=dt_str, count=self.idlen)).decode(sys_default_enc).replace('\x00','') for _ in range(nlinks)] 
            self.node_names = np.array(nodenames)
            self.link_names = np.array(linknames)
            linkstart = np.array(np.fromfile(fin, dtype=np.int32, count=nlinks), dtype=int)
            linkend = np.array(np.fromfile(fin, dtype=np.int32, count=nlinks), dtype=int)
            linktype = np.fromfile(fin, dtype=np.int32, count=nlinks)
            self._linktype = linktype
            tankidxs = np.fromfile(fin, dtype=np.int32, count=ntanks)
            tankarea = np.fromfile(fin, dtype=np.dtype(ftype), count=ntanks)
            elevation = np.fromfile(fin, dtype=np.dtype(ftype), count=nnodes)
            linklen = np.fromfile(fin, dtype=np.dtype(ftype), count=nlinks)
            diameter = np.fromfile(fin, dtype=np.dtype(ftype), count=nlinks)
            """
            self.save_network_desc_line('link_start', linkstart)
            self.save_network_desc_line('link_end', linkend)
            self.save_network_desc_line('link_type', linktype)
            self.save_network_desc_line('tank_node_index', tankidxs)
            self.save_network_desc_line('tank_area', tankarea)
            self.save_network_desc_line('node_elevation', elevation)
            self.save_network_desc_line('link_length', linklen)
            self.save_network_desc_line('link_diameter', diameter)
            """
            logger.debug('... read energy data ...')
            for i in range(npumps):
                pidx = int(np.fromfile(fin,dtype=np.int32, count=1)[0])
                energy = np.fromfile(fin, dtype=np.dtype(ftype), count=6)
                self.save_energy_line(pidx, linknames[pidx-1], energy)
            peakenergy = np.fromfile(fin, dtype=np.dtype(ftype), count=1)
            self.peak_energy = peakenergy

            logger.debug('... read EP simulation data ...')
            reporttimes = np.arange(reportstart, duration+reportstep-(duration%reportstep), reportstep)
            nrptsteps = len(reporttimes)
            statsN = nrptsteps
            if statsflag in [StatisticsType.Maximum, StatisticsType.Minimum, StatisticsType.Range]:
                nrptsteps = 1
                reporttimes = [reportstart + reportstep]
            self.num_periods = nrptsteps
            self.report_times = reporttimes

            # set up results metadata dictionary
            """
            if wqopt == QualType.Age:
                self.results.meta['quality_mode'] = 'AGE'
                self.results.meta['quality_units'] = 's'
            elif wqopt == QualType.Trace:
                self.results.meta['quality_mode'] = 'TRACE'
                self.results.meta['quality_units'] = '%'
                self.results.meta['quality_trace'] = srctrace
            elif wqopt == QualType.Chem:
                self.results.meta['quality_mode'] = 'CHEMICAL'
                self.results.meta['quality_units'] = wqunits
                self.results.meta['quality_chem'] = chemical
            self.results.time = reporttimes
            self.save_network_desc_line('report_times', reporttimes)
            self.save_network_desc_line('node_elevation', pd.Series(data=elevation, index=nodenames))
            self.save_network_desc_line('link_length', pd.Series(data=linklen, index=linknames))
            self.save_network_desc_line('link_diameter', pd.Series(data=diameter, index=linknames))
            self.save_network_desc_line('stats_mode', statsflag)
            self.save_network_desc_line('stats_N', statsN)
            nodetypes = np.array(['Junction']*self.num_nodes, dtype='|S10')
            nodetypes[tankidxs-1] = 'Tank'
            nodetypes[tankidxs[tankarea==0]-1] = 'Reservoir'
            linktypes = np.array(['Pipe']*self.num_links)
            linktypes[ linktype == EN.PUMP ] = 'Pump'
            linktypes[ linktype > EN.PUMP ] = 'Valve'
            self.save_network_desc_line('link_type', pd.Series(data=linktypes, index=linknames, copy=True))
            linktypes[ linktype == EN.CVPIPE ] = 'CV'
            linktypes[ linktype == EN.FCV ] = 'FCV'
            linktypes[ linktype == EN.PRV ] = 'PRV'
            linktypes[ linktype == EN.PSV ] = 'PSV'
            linktypes[ linktype == EN.PBV ] = 'PBV'
            linktypes[ linktype == EN.TCV ] = 'TCV'
            linktypes[ linktype == EN.GPV ] = 'GPV'
            self.save_network_desc_line('link_subtype', pd.Series(data=linktypes, index=linknames, copy=True))
            self.save_network_desc_line('node_type', pd.Series(data=nodetypes, index=nodenames, copy=True))
            self.save_network_desc_line('node_names', np.array(nodenames, dtype=str))
            self.save_network_desc_line('link_names', np.array(linknames, dtype=str))
            names = np.array(nodenames, dtype=str)
            self.save_network_desc_line('link_start', pd.Series(data=names[linkstart-1], index=linknames, copy=True))
            self.save_network_desc_line('link_end', pd.Series(data=names[linkend-1], index=linknames, copy=True))
            """

#           type_list = 4*nnodes*['node'] + 8*nlinks*['link']
            name_list = nodenames*4 + linknames*8
            valuetype = nnodes*['demand']+nnodes*['head']+nnodes*['pressure']+nnodes*['quality'] + nlinks*['flow']+nlinks*['velocity']+nlinks*['headloss']+nlinks*['linkquality']+nlinks*['linkstatus']+nlinks*['linksetting']+nlinks*['reactionrate']+nlinks*['frictionfactor']

#           tuples = zip(type_list, valuetype, name_list)
            tuples = list(zip(valuetype, name_list))
#                tuples = [(valuetype[i], v) for i, v in enumerate(name_list)]
            index = pd.MultiIndex.from_tuples(tuples, names=['value','name'])

            try:
                data = np.fromfile(fin, dtype = np.dtype(ftype), count = (4*nnodes+8*nlinks)*nrptsteps)
            except Exception as e:
                logger.exception('Failed to process file: %s', e)

            N = int(np.floor(len(data)/(4*nnodes+8*nlinks)))
            if N < nrptsteps:
                t = reporttimes[N]
                if convergence_error:
                    logger.error('Simulation did not converge at time ' + self._get_time(t) + '.')
                    raise RuntimeError('Simulation did not converge at time ' + self._get_time(t) + '.')
                else:
                    data = data[0:N*(4*nnodes+8*nlinks)]
                    data = np.reshape(data, (N, (4*nnodes+8*nlinks)))
                    reporttimes = reporttimes[0:N]
                    warnings.warn('Simulation did not converge at time ' + self._get_time(t) + '.')
                    self.results.error_code = ResultsStatus.error
            else:
                data = np.reshape(data, (nrptsteps, (4*nnodes+8*nlinks)))
                self.results.error_code = None

            df = pd.DataFrame(data.transpose(), index =index, columns = reporttimes)
            df = df.transpose()

            self.results.node = {}
            self.results.link = {}
            self.results.network_name = self.inp_file

            if convert:
                # Node Results
                self.results.node['demand'] = HydParam.Demand._to_si(self.flow_units, df['demand'])
                self.results.node['head'] = HydParam.HydraulicHead._to_si(self.flow_units, df['head'])
                self.results.node['pressure'] = HydParam.Pressure._to_si(self.flow_units, df['pressure'])

                # Water Quality Results (node and link)
                if self.quality_type is QualType.Chem:
                    self.results.node['quality'] = QualParam.Concentration._to_si(self.flow_units, df['quality'], mass_units=self.mass_units)
                    self.results.link['quality'] = QualParam.Concentration._to_si(self.flow_units, df['linkquality'], mass_units=self.mass_units)
                elif self.quality_type is QualType.Age:
                    self.results.node['quality'] = QualParam.WaterAge._to_si(self.flow_units, df['quality'], mass_units=self.mass_units)
                    self.results.link['quality'] = QualParam.WaterAge._to_si(self.flow_units, df['linkquality'], mass_units=self.mass_units)
                else:
                    self.results.node['quality'] = df['quality']
                    self.results.link['quality'] = df['linkquality']

                # Link Results
                self.results.link['flowrate'] = HydParam.Flow._to_si(self.flow_units, df['flow'])
                self.results.link['velocity'] = HydParam.Velocity._to_si(self.flow_units, df['velocity'])

                headloss = np.array(df['headloss'])
                headloss[:, linktype < 2] = to_si(self.flow_units, headloss[:, linktype < 2], HydParam.HeadLoss) # Pipe or CV
                headloss[:, linktype >= 2] = to_si(self.flow_units, headloss[:, linktype >= 2], HydParam.Length) # Pump or Valve
                self.results.link["headloss"] = pd.DataFrame(data=headloss, columns=linknames, index=reporttimes)

                status = np.array(df['linkstatus'])
                if self.convert_status:
                    status[status <= 2] = 0
                    status[status == 3] = 1
                    status[status >= 5] = 1
                    status[status == 4] = 2
                self.results.link['status'] = pd.DataFrame(data=status, columns=linknames, index=reporttimes)

                setting = np.array(df['linksetting'])
                # pump setting is relative speed (unitless)
                setting[:, linktype == EN.PIPE] = to_si(self.flow_units, setting[:, linktype == EN.PIPE], HydParam.RoughnessCoeff, 
                                                darcy_weisbach=darcy_weisbach)
                setting[:, linktype == EN.PRV] = to_si(self.flow_units, setting[:, linktype == EN.PRV], HydParam.Pressure)
                setting[:, linktype == EN.PSV] = to_si(self.flow_units, setting[:, linktype == EN.PSV], HydParam.Pressure)
                setting[:, linktype == EN.PBV] = to_si(self.flow_units, setting[:, linktype == EN.PBV], HydParam.Pressure)
                setting[:, linktype == EN.FCV] = to_si(self.flow_units, setting[:, linktype == EN.FCV], HydParam.Flow)
                self.results.link['setting'] = pd.DataFrame(data=setting, columns=linknames, index=reporttimes)

                self.results.link['friction_factor'] = df['frictionfactor']
                self.results.link['reaction_rate'] = QualParam.ReactionRate._to_si(self.flow_units, df['reactionrate'],self.mass_units) 
            else:
                self.results.node['demand'] = df['demand']
                self.results.node['head'] = df['head']
                self.results.node['pressure'] = df['pressure']
                self.results.node['quality'] = df['quality']

                self.results.link['flowrate'] = df['flow']
                self.results.link['headloss'] = df['headloss']
                self.results.link['velocity'] = df['velocity']
                self.results.link['quality'] = df['linkquality']
                self.results.link['status'] = df['linkstatus']
                self.results.link['setting'] = df['linksetting']
                self.results.link['friction_factor'] = df['frictionfactor']
                self.results.link['reaction_rate'] = df['reactionrate']

            logger.debug('... read epilog ...')
            # Read the averages and then the number of periods for checks
            averages = np.fromfile(fin, dtype=np.dtype(ftype), count=4)
            self.averages = averages
            np.fromfile(fin, dtype=np.int32, count=1)
            warnflag = np.fromfile(fin, dtype=np.int32, count=1)
            magic2 = np.fromfile(fin, dtype=np.int32, count=1)
            if magic1 != magic2:
                logger.critical('The magic number did not match -- binary incomplete or incorrectly read. If you believe this file IS complete, please try a different float type. Current type is "%s"',ftype)
            #print numperiods, warnflag, magic
            if warnflag != 0:
                logger.warning('Warnings were issued during simulation')
        self.finalize_save(magic1==magic2, warnflag)

        return self.results