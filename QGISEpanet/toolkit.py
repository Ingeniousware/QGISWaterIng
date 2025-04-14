"""
The wntr.epanet.toolkit module is a Python extension for the EPANET 
Programmers Toolkit DLLs.
"""
import ctypes
import logging
import os
import os.path
import platform
import sys
from ctypes import byref, c_int, create_string_buffer

import numpy as np
from pkg_resources import resource_filename

from .exceptions import EN_ERROR_CODES, EpanetException
from .util import EN, SizeLimits


logger = logging.getLogger(__name__)

epanet_toolkit = "wntr.epanet.toolkit"

if os.name in ["nt", "dos"]:
    libepanet = "libepanet/windows-x64/epanet22.dll"
elif sys.platform in ["darwin"]:
    if 'arm' in platform.platform().lower():
        libepanet = "libepanet/darwin-arm/libepanet2.dylib"
    else:
        libepanet = "libepanet/darwin-x64/libepanet22.dylib"
else:
    libepanet = "libepanet/linux-x64/libepanet22.so"


def ENgetwarning(code, sec=-1):
    if sec >= 0:
        hours = int(sec / 3600.0)
        sec -= hours * 3600
        mm = int(sec / 60.0)
        sec -= mm * 60
        header = "%3d:%.2d:%.2d" % (hours, mm, sec)
    else:
        header = "{}".format(code)
    if code < 100:
        msg = EN_ERROR_CODES.get(code, "Unknown warning %s")
    else:
        raise EpanetException(code)

    return msg % header


def runepanet(inpfile, rptfile=None, binfile=None):
    """Run an EPANET command-line simulation

    Parameters
    ----------
    inpfile : str
        The input file name
    """
    file_prefix, file_ext = os.path.splitext(inpfile)
    if rptfile is None:
        rptfile = file_prefix + ".rpt"
    if binfile is None:
        binfile = file_prefix + ".bin"

    enData = ENepanet()
    enData.ENopen(inpfile, rptfile, binfile)
    enData.ENsolveH()
    enData.ENsolveQ()
    try:
        enData.ENreport()
    except:
        pass
    enData.ENclose()


class ENepanet:
    """Wrapper class to load the EPANET DLL object, then perform operations on
    the EPANET object that is created when a file is loaded.

    This simulator is thread safe **only** for EPANET `version=2.2`.

    Parameters
    ----------
    inpfile : str
        Input file to use
    rptfile : str
        Output file to report to
    binfile : str
        Results file to generate
    version : float
        EPANET version to use (either 2.0 or 2.2)
    """

    def __init__(self, inpfile="", rptfile="", binfile="", version=2.2):
        self.ENlib = None
        self.errcode = 0
        self.errcodelist = []
        self.cur_time = 0

        self.Warnflag = False
        self.Errflag = False
        self.fileLoaded = False

        self.inpfile = inpfile
        self.rptfile = rptfile
        self.binfile = binfile
        
         # Link types
        self.TYPELINK = ['CVPIPE', 'PIPE', 'PUMP', 'PRV', 'PSV',
                         'PBV', 'FCV', 'TCV', 'GPV']

        try:
            if float(version) == 2.0:
                libname = libepanet.replace('epanet22.','epanet20.')
                if 'arm' in platform.platform():
                    raise NotImplementedError('ARM-based processors not supported for version 2.0 of EPANET. Please use version=2.2')
            else:
                libname = libepanet
            libname = resource_filename(__name__, libname)
            if os.name in ["nt", "dos"]:
                self.ENlib = ctypes.windll.LoadLibrary(libname)
            else:
                self.ENlib = ctypes.cdll.LoadLibrary(libname)
        except:
            raise
        finally:
            if version >= 2.2:
                self._project = ctypes.c_uint64()
            else:
                self._project = None
        return

    def isOpen(self):
        """Checks to see if the file is open"""
        return self.fileLoaded

    def _error(self, *args):
        """Print the error text the corresponds to the error code returned"""
        if not self.errcode:
            return
        # errtxt = self.ENlib.ENgeterror(self.errcode)
        errtext = EN_ERROR_CODES.get(self.errcode, "unknown error")
        if "%" in errtext and len(args) == 1:
            errtext % args
        if self.errcode >= 100:
            self.Errflag = True
            logger.error("EPANET error {} - {}".format(self.errcode, errtext))
            raise EpanetException(self.errcode)
        else:
            self.Warnflag = True
            # warnings.warn(ENgetwarning(self.errcode))
            logger.warning("EPANET warning {} - {}".format(self.errcode, ENgetwarning(self.errcode, self.cur_time)))
            self.errcodelist.append(ENgetwarning(self.errcode, self.cur_time))
        return

    def ENopen(self, inpfile=None, rptfile=None, binfile=None):
        """
        Opens an EPANET input file and reads in network data

        Parameters
        ----------
        inpfile : str
            EPANET INP file (default to constructor value)
        rptfile : str
            Output file to create (default to constructor value)
        binfile : str
            Binary output file to create (default to constructor value)
        """
        if self._project is not None:
            if self.fileLoaded:
                self.EN_close(self._project)
            if self.fileLoaded:
                raise RuntimeError("File is loaded and cannot be closed")
            if inpfile is None:
                inpfile = self.inpfile
            if rptfile is None:
                rptfile = self.rptfile
            if binfile is None:
                binfile = self.binfile
            inpfile = inpfile.encode("latin-1")
            rptfile = rptfile.encode("latin-1")
            binfile = binfile.encode("latin-1")
            self.ENlib.EN_createproject(ctypes.byref(self._project))
            self.errcode = self.ENlib.EN_open(self._project, inpfile, rptfile, binfile)
            self._error()
            if self.errcode < 100:
                self.fileLoaded = True
            return
        else:
            if self.fileLoaded:
                self.ENclose()
            if self.fileLoaded:
                raise RuntimeError("File is loaded and cannot be closed")
            if inpfile is None:
                inpfile = self.inpfile
            if rptfile is None:
                rptfile = self.rptfile
            if binfile is None:
                binfile = self.binfile
            inpfile = inpfile.encode("latin-1")
            rptfile = rptfile.encode("latin-1")
            binfile = binfile.encode("latin-1")
            self.errcode = self.ENlib.ENopen(inpfile, rptfile, binfile)
            self._error()
            if self.errcode < 100:
                self.fileLoaded = True
            return

    def ENclose(self):
        """Frees all memory and files used by EPANET"""
        if self._project is not None:
            self.errcode = self.ENlib.EN_close(self._project)
            self.ENlib.EN_deleteproject(self._project)
            self._project = None
            self._project = ctypes.c_uint64()
        else:
            self.errcode = self.ENlib.ENclose()
        self._error()
        if self.errcode < 100:
            self.fileLoaded = False
        return

    def ENsolveH(self):
        """Solves for network hydraulics in all time periods"""
        if self._project is not None:
            self.errcode = self.ENlib.EN_solveH(self._project)
        else:
            self.errcode = self.ENlib.ENsolveH()
        self._error()
        return

    def ENsaveH(self):
        """Solves for network hydraulics in all time periods

        Must be called before ENreport() if no water quality simulation made.
        Should not be called if ENsolveQ() will be used.
        """
        if self._project is not None:
            self.errcode = self.ENlib.EN_saveH(self._project)
        else:
            self.errcode = self.ENlib.ENsaveH()
        self._error()
        return

    def ENopenH(self):
        """Sets up data structures for hydraulic analysis"""
        if self._project is not None:
            self.errcode = self.ENlib.EN_openH(self._project)
        else:
            self.errcode = self.ENlib.ENopenH()
        self._error()
        return

    def ENinitH(self, iFlag):
        """Initializes hydraulic analysis

        Parameters
        -----------
        iFlag : 2-digit flag
            2-digit flag where 1st (left) digit indicates
            if link flows should be re-initialized (1) or
            not (0) and 2nd digit indicates if hydraulic
            results should be saved to file (1) or not (0)
        """
        if self._project is not None:
            self.errcode = self.ENlib.EN_initH(self._project, iFlag)
        else:
            self.errcode = self.ENlib.ENinitH(iFlag)
        self._error()
        return

    def ENrunH(self):
        """Solves hydraulics for conditions at time t

        This function is used in a loop with ENnextH() to run
        an extended period hydraulic simulation.
        See ENsolveH() for an example.

        Returns
        --------
        int
            Current simulation time (seconds)
        """
        lT = ctypes.c_long()
        if self._project is not None:
            self.errcode = self.ENlib.EN_runH(self._project, byref(lT))
        else:
            self.errcode = self.ENlib.ENrunH(byref(lT))
        self._error()
        self.cur_time = lT.value
        return lT.value

    def ENnextH(self):
        """Determines time until next hydraulic event

        This function is used in a loop with ENrunH() to run
        an extended period hydraulic simulation.
        See ENsolveH() for an example.

        Returns
        ---------
        int
            Time (seconds) until next hydraulic event (0 marks end of simulation period)
        """
        lTstep = ctypes.c_long()
        if self._project is not None:
            self.errcode = self.ENlib.EN_nextH(self._project, byref(lTstep))
        else:
            self.errcode = self.ENlib.ENnextH(byref(lTstep))
        self._error()
        return lTstep.value

    def ENcloseH(self):
        """Frees data allocated by hydraulics solver"""
        if self._project is not None:
            self.errcode = self.ENlib.EN_closeH(self._project)
        else:
            self.errcode = self.ENlib.ENcloseH()
        self._error()
        return

    def ENsavehydfile(self, filename):
        """Copies binary hydraulics file to disk

        Parameters
        -------------
        filename : str
            Name of hydraulics file to output
        """
        if self._project is not None:
            self.errcode = self.ENlib.EN_savehydfile(self._project, filename.encode("latin-1"))
        else:
            self.errcode = self.ENlib.ENsavehydfile(filename.encode("latin-1"))
        self._error()
        return

    def ENusehydfile(self, filename):
        """Opens previously saved binary hydraulics file

        Parameters
        -------------
        filename : str
            Name of hydraulics file to use
        """
        if self._project is not None:
            self.errcode = self.ENlib.EN_usehydfile(self._project, filename.encode("latin-1"))
        else:
            self.errcode = self.ENlib.ENusehydfile(filename.encode("latin-1"))
        self._error()
        return

    def ENsolveQ(self):
        """Solves for network water quality in all time periods"""
        if self._project is not None:
            self.errcode = self.ENlib.EN_solveQ(self._project)
        else:
            self.errcode = self.ENlib.ENsolveQ()
        self._error()
        return

    def ENopenQ(self):
        """Sets up data structures for water quality analysis"""
        if self._project is not None:
            self.errcode = self.ENlib.EN_openQ(self._project)
        else:
            self.errcode = self.ENlib.ENopenQ()
        self._error()
        return

    def ENinitQ(self, iSaveflag):
        """Initializes water quality analysis

        Parameters
        -------------
        iSaveflag : int
             EN_SAVE (1) if results saved to file, EN_NOSAVE (0) if not
        """
        if self._project is not None:
            self.errcode = self.ENlib.EN_initQ(self._project, iSaveflag)
        else:
            self.errcode = self.ENlib.ENinitQ(iSaveflag)
        self._error()
        return

    def ENrunQ(self):
        """Retrieves hydraulic and water quality results at time t

        This function is used in a loop with ENnextQ() to run
        an extended period water quality simulation. See ENsolveQ() for
        an example.

        Returns
        -------
        int
            Current simulation time (seconds)
        """
        lT = ctypes.c_long()
        if self._project is not None:
            self.errcode = self.ENlib.EN_runQ(self._project, byref(lT))
        else:
            self.errcode = self.ENlib.ENrunQ(byref(lT))
        self._error()
        return lT.value

    def ENnextQ(self):
        """Advances water quality simulation to next hydraulic event

        This function is used in a loop with ENrunQ() to run
        an extended period water quality simulation. See ENsolveQ() for
        an example.

        Returns
        --------
        int
            Time (seconds) until next hydraulic event (0 marks end of simulation period)
        """
        lTstep = ctypes.c_long()
        if self._project is not None:
            self.errcode = self.ENlib.EN_nextQ(self._project, byref(lTstep))
        else:
            self.errcode = self.ENlib.ENnextQ(byref(lTstep))
        self._error()
        return lTstep.value

    def ENcloseQ(self):
        """Frees data allocated by water quality solver"""
        if self._project is not None:
            self.errcode = self.ENlib.EN_closeQ(self._project)
        else:
            self.errcode = self.ENlib.ENcloseQ()
        self._error()
        return

    def ENreport(self):
        """Writes report to report file"""
        if self._project is not None:
            self.errcode = self.ENlib.EN_report(self._project)
        else:
            self.errcode = self.ENlib.ENreport()
        self._error()
        return

    def ENgetcount(self, iCode):
        """Retrieves the number of components of a given type in the network

        Parameters
        -------------
        iCode : int
            Component code (see toolkit.optComponentCounts)

        Returns
        ---------
        int
            Number of components in network

        """
        iCount = ctypes.c_int()
        if self._project is not None:
            self.errcode = self.ENlib.EN_getcount(self._project, iCode, byref(iCount))
        else:
            self.errcode = self.ENlib.ENgetcount(iCode, byref(iCount))
        self._error()
        return iCount.value

    def ENgetflowunits(self):
        """Retrieves flow units code

        Returns
        -----------
        Code of flow units in use (see toolkit.optFlowUnits)

        """
        iCode = ctypes.c_int()
        if self._project is not None:
            self.errcode = self.ENlib.EN_getflowunits(self._project, byref(iCode))
        else:
            self.errcode = self.ENlib.ENgetflowunits(byref(iCode))
        self._error()
        return iCode.value

    def ENgetnodeid(self, iIndex):
        """Gets the ID name of a node given its index.

        Parameters
        ----------
        iIndex : int
            a node's index (starting from 1).

        Returns
        -------
        str
            the node name
        """
        fValue = ctypes.create_string_buffer(SizeLimits.EN_MAX_ID.value)
        if self._project is not None:
            self.errcode = self.ENlib.EN_getnodeid(self._project, iIndex, byref(fValue))
        else:
            self.errcode = self.ENlib.ENgetnodeid(iIndex, byref(fValue))
        self._error()
        return str(fValue.value, "UTF-8")

    def ENgetnodeindex(self, sId):
        """Retrieves index of a node with specific ID

        Parameters
        -------------
        sId : int
            Node ID

        Returns
        ---------
        Index of node in list of nodes

        """
        iIndex = ctypes.c_int()
        if self._project is not None:
            self.errcode = self.ENlib.EN_getnodeindex(self._project, sId.encode("latin-1"), byref(iIndex))
        else:
            self.errcode = self.ENlib.ENgetnodeindex(sId.encode("latin-1"), byref(iIndex))
        self._error()
        return iIndex.value

    def ENgetnodetype(self, iIndex):
        """Retrieves a node's type given its index.

        Parameters
        ----------
        iIndex : int
            The index of the node

        Returns
        -------
        int
            the node type as an integer
        """
        fValue = ctypes.c_int()
        if self._project is not None:
            self.errcode = self.ENlib.EN_getnodetype(self._project, iIndex, byref(fValue))
        else:
            self.errcode = self.ENlib.ENgetnodetype(iIndex, byref(fValue))
        self._error()
        return fValue.value

    def ENgetnodevalue(self, iIndex, iCode):
        """Retrieves parameter value for a node

        Parameters
        -------------
        iIndex: int
            Node index
        iCode : int
            Node parameter code (see toolkit.optNodeParams)

        Returns
        ---------
        Value of node's parameter

        """
        fValue = ctypes.c_float()
        if self._project is not None:
            fValue = ctypes.c_double()
            self.errcode = self.ENlib.EN_getnodevalue(self._project, iIndex, iCode, byref(fValue))
        else:
            self.errcode = self.ENlib.ENgetnodevalue(iIndex, iCode, byref(fValue))
        self._error()
        return fValue.value

    def ENgetlinktype(self, iIndex):
        """Retrieves a link's type given its index.

        Parameters
        ----------
        iIndex : int
            The index of the link

        Returns
        -------
        int
            the link type as an integer
        """
        fValue = ctypes.c_int()
        if self._project is not None:
            self.errcode = self.ENlib.EN_getlinktype(self._project, iIndex, byref(fValue))
        else:
            self.errcode = self.ENlib.EN_getlinktype(iIndex, byref(fValue))
        self._error()
        return fValue.value


    def ENgetlinkindex(self, sId):
        """Retrieves index of a link with specific ID

        Parameters
        -------------
        sId : int
            Link ID

        Returns
        ---------
        Index of link in list of links

        """
        iIndex = ctypes.c_int()
        if self._project is not None:
            self.errcode = self.ENlib.EN_getlinkindex(self._project, sId.encode("latin-1"), byref(iIndex))
        else:
            self.errcode = self.ENlib.ENgetlinkindex(sId.encode("latin-1"), byref(iIndex))
        self._error()
        return iIndex.value

    def ENgetlinkvalue(self, iIndex, iCode):
        """Retrieves parameter value for a link

        Parameters
        -------------
        iIndex : int
            Link index
        iCode : int
            Link parameter code (see toolkit.optLinkParams)

        Returns
        ---------
        Value of link's parameter

        """
        fValue = ctypes.c_float()
        if self._project is not None:
            fValue = ctypes.c_double()
            self.errcode = self.ENlib.EN_getlinkvalue(self._project, iIndex, iCode, byref(fValue))
        else:
            self.errcode = self.ENlib.ENgetlinkvalue(iIndex, iCode, byref(fValue))
        self._error()
        return fValue.value

    def ENsetlinkvalue(self, iIndex, iCode, fValue):
        """Set the value on a link

        Parameters
        ----------
        iIndex : int
            the link index
        iCode : int
            the parameter enum integer
        fValue : float
            the value to set on the link
        """
        if self._project is not None:
            self.errcode = self.ENlib.EN_setlinkvalue(
                self._project, ctypes.c_int(iIndex), ctypes.c_int(iCode), ctypes.c_double(fValue)
            )
        else:
            self.errcode = self.ENlib.ENsetlinkvalue(ctypes.c_int(iIndex), ctypes.c_int(iCode), ctypes.c_float(fValue))
        self._error()

    def ENsetnodevalue(self, iIndex, iCode, fValue):
        """
        Set the value on a node

        Parameters
        ----------
        iIndex : int
            the node index
        iCode : int
            the parameter enum integer
        fValue : float
            the value to set on the node
        """
        if self._project is not None:
            self.errcode = self.ENlib.EN_setnodevalue(
                self._project, ctypes.c_int(iIndex), ctypes.c_int(iCode), ctypes.c_double(fValue)
            )
        else:
            self.errcode = self.ENlib.ENsetnodevalue(ctypes.c_int(iIndex), ctypes.c_int(iCode), ctypes.c_float(fValue))
        self._error()

    def ENsettimeparam(self, eParam, lValue):
        """Set a time parameter value

        Parameters
        ----------
        eParam : int
            the time parameter to set
        lValue : long
            the value to set, in seconds
        """
        if self._project is not None:
            self.errcode = self.ENlib.EN_settimeparam(self._project, ctypes.c_int(eParam), ctypes.c_long(lValue))
        else:
            self.errcode = self.ENlib.ENsettimeparam(ctypes.c_int(eParam), ctypes.c_long(lValue))
        self._error()

    def ENgettimeparam(self, eParam):
        """Get a time parameter value

        Parameters
        ----------
        eParam : int
            the time parameter to get

        Returns
        -------
        long
            the value of the time parameter, in seconds
        """
        lValue = ctypes.c_long()
        if self._project is not None:
            self.errcode = self.ENlib.EN_gettimeparam(self._project, ctypes.c_int(eParam), byref(lValue))
        else:
            self.errcode = self.ENlib.ENgettimeparam(ctypes.c_int(eParam), byref(lValue))
        self._error()
        return lValue.value

    def ENaddcontrol(self, iType: int, iLinkIndex: int, dSetting: float, iNodeIndex: int, dLevel: float) -> int:
        """Add a new simple control

        Parameters
        ----------
        iType : int
            the type of control
        iLinkIndex : int
            the index of the link
        dSetting : float
            the new link setting value
        iNodeIndex : int
            Set to 0 for time of day or timer
        dLevel : float
            the level to compare against

        Returns
        -------
        int
            the new control number
        """
        lValue = ctypes.c_int()
        if self._project is not None:
            self.errcode = self.ENlib.EN_addcontrol(
                self._project,
                ctypes.c_int(iType),
                ctypes.c_int(iLinkIndex),
                ctypes.c_double(dSetting),
                ctypes.c_int(iNodeIndex),
                ctypes.c_double(dLevel),
                byref(lValue),
            )
        else:
            self.errcode = self.ENlib.ENaddcontrol(
                ctypes.c_int(iType),
                ctypes.c_int(iLinkIndex),
                ctypes.c_double(dSetting),
                ctypes.c_int(iNodeIndex),
                ctypes.c_double(dLevel),
                byref(lValue),
            )
        self._error()
        return lValue.value

    def ENgetcontrol(self, iIndex: int):
        """Get values defined by a control.

        Parameters
        ----------
        iIndex : int
            the control number
        """
        iType = ctypes.c_int()
        iLinkIndex = ctypes.c_int()
        dSetting = ctypes.c_double()
        iNodeIndex = ctypes.c_int()
        dLevel = ctypes.c_double()
        if self._project is not None:
            self.errcode = self.ENlib.EN_getcontrol(
                self._project,
                ctypes.c_int(iIndex),
                byref(iType),
                byref(iLinkIndex),
                byref(dSetting),
                byref(iNodeIndex),
                byref(dLevel),
            )
        else:
            self.errcode = self.ENlib.ENgetcontrol(
                ctypes.c_int(iIndex), byref(iType), byref(iLinkIndex), byref(dSetting), byref(iNodeIndex), byref(dLevel)
            )
        self._error()
        return dict(
            index=iIndex,
            type=iType.value,
            linkindex=iLinkIndex.value,
            setting=dSetting.value,
            nodeindex=iNodeIndex.value,
            level=dLevel.value,
        )

    def ENsetcontrol(self, iIndex: int, iType: int, iLinkIndex: int, dSetting: float, iNodeIndex: int, dLevel: float):
        """Change values on a simple control

        Parameters
        ----------
        iIndex : int
            the control index
        iType : int
            the type of control comparison
        iLinkIndex : int
            the link being changed
        dSetting : float
            the setting to change to
        iNodeIndex : int
            the node being compared against, Set to 0 for time of day or timer
        dLevel : float
            the level being checked

        Warning
        -------
        There is an error in EPANET 2.2 that sets the `dLevel` parameter to 0.0 on Macs
        regardless of the value the user passes in. This means that to use this toolkit
        functionality on a Mac, the user must delete and create a new control to change
        the level.

        """
        if self._project is not None:
            try:
                self.errcode = self.ENlib.EN_setcontrol(
                    self._project,
                    ctypes.c_int(iIndex),
                    ctypes.c_int(iType),
                    ctypes.c_int(iLinkIndex),
                    ctypes.c_double(dSetting),
                    ctypes.c_int(iNodeIndex),
                    ctypes.c_double(dLevel),
                )
            except:
                self.errcode = self.ENlib.EN_setcontrol(
                    self._project,
                    ctypes.c_int(iIndex),
                    ctypes.c_int(iType),
                    ctypes.c_int(iLinkIndex),
                    ctypes.c_double(dSetting),
                    ctypes.c_int(iNodeIndex),
                    ctypes.c_float(dLevel),
                )
        else:
            self.errcode = self.ENlib.ENsetcontrol(
                ctypes.c_int(iIndex),
                ctypes.c_int(iType),
                ctypes.c_int(iLinkIndex),
                ctypes.c_double(dSetting),
                ctypes.c_int(iNodeIndex),
                ctypes.c_double(dLevel),
            )
        self._error()

    def ENdeletecontrol(self, iControlIndex):
        """Delete a control.

        Parameters
        ----------
        iControlIndex : int
            the simple control to delete
        """
        if self._project is not None:
            self.errcode = self.ENlib.EN_deletecontrol(self._project, ctypes.c_int(iControlIndex))
        else:
            self.errcode = self.ENlib.ENdeletecontrol(ctypes.c_int(iControlIndex))
        self._error()

    def ENsaveinpfile(self, inpfile):
        """Saves EPANET input file

        Parameters
        -------------
        inpfile : str
                    EPANET INP output file

        """

        inpfile = inpfile.encode("latin-1")
        if self._project is not None:
            self.errcode = self.ENlib.EN_saveinpfile(self._project, inpfile)
        else:
            self.errcode = self.ENlib.ENsaveinpfile(inpfile)
        self._error()

        return

# ================= INICIO ====================================================================================

    def __getNodeJunctionIndices(self, *argv):
        if len(argv) == 0:
            numJuncs = self.getNodeJunctionCount()
            return list(range(1, numJuncs + 1))
        else:
            return argv[0]


    def isList(var):
        if isinstance(var, (list, np.ndarray, np.matrix)):
            return True
        else:
            return False


    def getNodeCount(self):
        """ Retrieves the number of nodes.

        Example:

        >>> d.getNodeCount()

        See also getNodeIndex, getLinkCount().
        """
        return self.ENgetcount(EN.NODECOUNT)


    def getNodeTypeIndex(self, *argv):
        """ Retrieves the node-type code for all nodes.

        Example:

        >>> d.getNodeTypeIndex()      # Retrieves the node-type code for all nodes
        >>> d.getNodeTypeIndex(1)     # Retrieves the node-type code for the first node

        See also getNodeNameID, getNodeIndex, getNodeType, getNodesInfo.
        """
        nTypes = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, list):
                for i in index:
                    nTypes.append(self.ENgetnodetype(i))
            else:
                nTypes = self.ENgetnodetype(index)
        else:
            for i in range(self.getNodeCount()):
                nTypes.append(self.ENgetnodetype(i + 1))
        return nTypes


    def getNodeJunctionCount(self):
        """ Retrieves the number of junction nodes.

        Example:

        >>> d.getNodeJunctionCount()

        See also getNodeTankCount, getNodeCount.
        """
        return self.getNodeTypeIndex().count(EN.JUNCTION)


    def getNodeJunctionIndex(self, *argv):
        """Retrieves the indices of junctions.

        Example:

        >>> d.getNodeJunctionIndex()          # Retrieves the indices of all junctions
        >>> d.getNodeJunctionIndex([1,2])     # Retrieves the indices of the first 2 junctions

        See also getNodeNameID, getNodeIndex, getNodeReservoirIndex,
        getNodeType, getNodeTypeIndex, getNodesInfo.
        """
        tmpNodeTypes = self.getNodeTypeIndex()
        value = [i for i, x in enumerate(tmpNodeTypes) if x == EN.JUNCTION]
        if (len(value) > 0) and (len(argv) > 0):
            index = argv[0]
            try:
                if isinstance(index, list):
                    jIndices = []
                    for i in index:
                        jIndices.append(value[i - 1] + 1)
                    return jIndices
                else:
                    return value[index - 1] + 1
            except:
                raise Exception('Some JUNCTION indices do not exist.')
        else:
            jIndices = value
            return [i + 1 for i in jIndices]


    def getNodeNameID(self, *argv):
        """ Retrieves the ID label of all nodes or some nodes with a specified index.

        Example 1:

        >>> d.getNodeNameID()                   # Retrieves the ID label of all nodes

        Example 2:

        >>> d.getNodeNameID(1)                  # Retrieves the ID label of the first node

        Example 3:

        >>> junctionIndex = d.getNodeJunctionIndex()
        >>> d.getNodeNameID(junctionIndex)       # Retrieves the ID labels of all junctions give their indices

        See also getNodeReservoirNameID, getNodeJunctionNameID,
        getNodeIndex, getNodeType, getNodesInfo.
        """
        values = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, list):
                for i in index:
                    values.append(self.ENgetnodeid(i))
            else:
                values = self.ENgetnodeid(index)
        else:
            for i in range(self.getNodeCount()):
                values.append(self.ENgetnodeid(i + 1))
        return values


    def getNodeJunctionNameID(self, *argv):
        """ Retrieves the junction ID label.

        Example:

        >>> d.getNodeJunctionNameID()       # Retrieves the ID of all junctions
        >>> d.getNodeJunctionNameID(1)      # Retrieves the ID of the 1st junction
        >>> d.getNodeJunctionNameID([1,2])  # Retrieves the ID of the first 2 junction

        See also getNodeNameID, getNodeReservoirNameID, getNodeIndex,
        getNodeJunctionIndex, getNodeType, getNodesInfo.
        """
        if len(argv) == 0:
            return self.getNodeNameID(self.getNodeJunctionIndex())
        else:
            indices = self.__getNodeJunctionIndices(*argv)
            if self.isList(indices):
                return [self.getNodeNameID(i) for i in indices]
            else:
                return self.getNodeNameID(indices)


    def getNodeReservoirIndex(self, *argv):
        """ Retrieves the indices of reservoirs.

        Example 1:

        >>> d.getNodeReservoirIndex()           # Retrieves the indices of all reservoirs.

        Example 2:

        >>> d.getNodeReservoirIndex([1,2,3])    # Retrieves the indices of the first 3 reservoirs, if they exist.

        See also getNodeNameID, getNodeIndex, getNodeJunctionIndex,
        getNodeType, getNodeTypeIndex, getNodesInfo.
        """
        tmpNodeTypes = self.getNodeTypeIndex()
        value = [i for i, x in enumerate(tmpNodeTypes) if x == EN.RESERVOIR]
        if (len(value) > 0) and (len(argv) > 0):
            index = argv[0]
            try:
                if isinstance(index, list):
                    rIndices = []
                    for i in index:
                        rIndices.append(value[i - 1] + 1)
                    return rIndices
                else:
                    return value[index - 1] + 1
            except:
                raise Exception('Some RESERVOIR indices do not exist.')
        else:
            rIndices = value
            return [i + 1 for i in rIndices]


    def getNodeReservoirNameID(self, *argv):
        """ Retrieves the reservoir ID label.

        Example :

        >>> d.getNodeReservoirNameID()       # Retrieves the ID of all reservoirs
        >>> d.getNodeReservoirNameID(1)      # Retrieves the ID of the 1st reservoir
        >>> d.getNodeReservoirNameID([1,2])  # Retrieves the ID of the first 2 reservoirs (if they exist!)

        See also getNodeNameID, getNodeJunctionNameID, getNodeIndex,
        getNodeReservoirIndex, getNodeType, getNodesInfo.
        """
        if len(argv) == 0:
            return self.getNodeNameID(self.getNodeReservoirIndex())
        else:
            indices = self.getNodeReservoirIndex(*argv)
            if self.isList(indices):
                return [self.getNodeNameID(i) for i in indices]
            else:
                return self.getNodeNameID(indices)


    def getLinkCount(self):
        """ Retrieves the number of links.

        Example:

        >>> d.getLinkCount()

        See also getLinkIndex, getNodeCount.
        """
        return self.ENgetcount(EN.LINKCOUNT)


    def ENgetlinkid(self, iIndex):
        """Gets the ID name of a link given its index.

        Parameters
        ----------
        iIndex : int
            a link's index (starting from 1).

        Returns
        -------
        str
            the link name
        """
        fValue = create_string_buffer(SizeLimits.EN_MAX_ID.value)
        if self._project is not None:
            self.errcode = self.ENlib.EN_getlinkid(self._project, int(iIndex), byref(fValue))
        else:
            self.errcode = self.ENlib.ENgetlinkid(int(iIndex), byref(fValue))
        self._error()
        return str(fValue.value, "UTF-8")


    def getLinkNameID(self, *argv):
        """ Retrieves the ID label(s) of all links, or the IDs of
        an index set of links.

        Example 1:

        # Retrieves the ID's of all links
        >>> d.getLinkNameID()

        Example 2:

        >>> linkIndex = 1
        # Retrieves the ID of the link with index = 1
        >>> d.getLinkNameID(linkIndex)

        Example 3:

        >>> linkIndices = [1,2,3]
        # Retrieves the IDs of the links with indices = 1, 2, 3
        >>> d.getLinkNameID(linkIndices)

        See also getNodeNameID, getLinkPipeNameID, getLinkIndex.
        """
        values = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                for i in index:
                    values.append(self.ENgetlinkid(i))
            else:
                values = self.ENgetlinkid(index)
        else:
            for i in range(self.getLinkCount()):
                values.append(self.ENgetlinkid(i + 1))
        return values


    def getLinkTypeIndex(self, *argv):
        """ Retrieves the link-type code for all links.

        Example:

        # Retrieves the link-type code for all links
        >>> d.getLinkTypeIndex()
        # Retrieves the link-type code for the first link
        >>> d.getLinkTypeIndex(1)
        # Retrieves the link-type code for the second and third links
        >>> d.getLinkTypeIndex([2,3])

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkLength, getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        lTypes = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, list):
                for i in index:
                    lTypes.append(self.ENgetlinktype(i))
            else:
                lTypes = self.ENgetlinktype(index)
        else:
            for i in range(self.getLinkCount()):
                lTypes.append(self.ENgetlinktype(i + 1))
        return lTypes


    def getLinkPumpIndex(self, *argv):
        """ Retrieves the pump indices.

        Example 1:

        >>> d.getLinkPumpIndex()          # Retrieves the indices of all pumps

        Example 2:

        >>> d.getLinkPumpIndex(1)         # Retrieves the index of the 1st pump

        Example 3:

        >>> d = epanet('Richmond_standard.inp')
        >>> d.getLinkPumpIndex([1,2])     # Retrieves the indices of the first 2 pumps

        See also getLinkIndex, getLinkPipeIndex, getLinkValveIndex.
        """
        tmpLinkTypes = self.getLinkTypeIndex()
        value = np.array([i for i, x in enumerate(tmpLinkTypes) if x == EN.PUMP]) + 1
        if value.size == 0:
            return value
        if argv:
            index = np.array(argv[0])
            try:
                return value[index - 1]
            except:
                raise Exception('Some PUMP indices do not exist.')
        else:
            return value


    def getLinkPumpNameID(self, *argv):
        """ Retrieves the pump ID.

        Example 1:

        >>> d.getLinkPumpNameID()          # Retrieves the ID's of all pumps

        Example 2:

        >>> d.getLinkPumpNameID(1)         # Retrieves the ID of the 1st pump

        Example 3:

        >>> d = epanet('Net3_trace.inp')
        >>> d.getLinkPumpNameID([1,2])     # Retrieves the ID of the first 2 pumps

        See also getLinkNameID, getLinkPipeNameID, getNodeNameID.
        """
        return self.getLinkNameID(self.getLinkPumpIndex(*argv))


    def ENgetlinknodes(self, index):
        """ Gets the indexes of a link's start- and end-nodes.

        ENgetlinknodes(index)

        Parameters:
        index      	a link's index (starting from 1).

        Returns:
        from   the index of the link's start node (starting from 1).
        to     the index of the link's end node (starting from 1).
        """
        fromNode = c_int()
        toNode = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getlinknodes(self._ph, int(index), byref(fromNode), byref(toNode))
        else:
            self.errcode = self._lib.ENgetlinknodes(int(index), byref(fromNode), byref(toNode))

        self._error()
        return [fromNode.value, toNode.value]