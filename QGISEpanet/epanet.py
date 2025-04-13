import logging
import os

from .toolkit import ENepanet
from .io import BinFile

logger = logging.getLogger(__name__)


class EpanetSimulator():
    def __init__(self, reader=None, result_types=None):
        self.reader = reader
        self.prep_time_before_main_loop = 0.0
        if self.reader is None:
            self.reader = BinFile(result_types=result_types)
        self._inp_file = None
        self._data = {
            'JunctionNameID': None,
            'ReservoirNameID': None,
            'PumpNameID': None }


    def run_sim(self, file_prefix, save_hyd=False, use_hyd=False, hydfile=None,
                version=2.2, convergence_error=False):

        """
        Run the EPANET simulator.

        Runs the EPANET simulator through the compiled toolkit DLL. Can use/save hydraulics
        to allow for separate WQ runs.

        .. note::

            By default, WNTR now uses the EPANET 2.2 toolkit as the engine for the EpanetSimulator.
            To force usage of the older EPANET 2.0 toolkit, use the ``version`` command line option.
            Note that if the demand_model option is set to PDD, then a warning will be issued, as
            EPANET 2.0 does not support such analysis.


        Parameters
        ----------
        file_prefix : str
            All files (.inp, .bin/.out, .hyd, .rpt) use this prefix
        use_hyd : bool
            Will load hydraulics from ``file_prefix + '.hyd'`` or from file specified in `hydfile_name`
        save_hyd : bool
            Will save hydraulics to ``file_prefix + '.hyd'`` or to file specified in `hydfile_name`
        hydfile : str
            Optionally specify a filename for the hydraulics file other than the `file_prefix`
        version : float
            {2.0, **2.2**} Optionally change the version of the EPANET toolkit libraries. Valid choices are
            either 2.2 (the default if no argument provided) or 2.0.
        convergence_error: bool (optional)
            If convergence_error is True, an error will be raised if the
            simulation does not converge. If convergence_error is False, partial results are returned, 
            a warning will be issued, and results.error_code will be set to 0
            if the simulation does not converge.  Default = False.
        """
        if isinstance(version, str):
            version = float(version)
        # direc = os.path.join(os.path.dirname(file_prefix), os.path.splitext(os.path.basename(file_prefix))[0])
        direc = file_prefix[:-4]
        # inpfile = file_prefix + '.inp'
        inpfile = file_prefix
        # write_inpfile(self._wn, inpfile, units=self._wn.options.hydraulic.inpfile_units, version=version)
        enData = ENepanet(version=version)
        self.enData = enData
        rptfile = direc + '.rpt'
        outfile = direc + '.bin'
        # if self._wn._msx is not None:
        #     save_hyd = True
        if hydfile is None:
            hydfile = direc + '.hyd'
        enData.ENopen(inpfile, rptfile, outfile)
        if use_hyd:
            enData.ENusehydfile(hydfile)
            logger.debug('Loaded hydraulics')
        else:
            enData.ENsolveH()
            self._data['JunctionNameID'] = enData.getNodeJunctionNameID()
            self._data['ReservoirNameID'] = enData.getNodeReservoirNameID()
            self._data['PumpNameID'] = enData.getLinkPumpNameID()
            
            logger.debug('Solved hydraulics')
        if save_hyd:
            enData.ENsavehydfile(hydfile)
            logger.debug('Saved hydraulics')
        enData.ENsolveQ()
        logger.debug('Solved quality')
        enData.ENreport()
        logger.debug('Ran quality')
        enData.ENclose()
        logger.debug('Completed run')
        #os.sys.stderr.write('Finished Closing\n')
        
        results = self.reader.read(outfile, convergence_error)

        return results


    def getNodeJunctionNameID(self):
        return self._data['JunctionNameID']


    def getNodeReservoirNameID(self):
        return self._data['ReservoirNameID']


    def getLinkPumpNameID(self):
        return self._data['PumpNameID']