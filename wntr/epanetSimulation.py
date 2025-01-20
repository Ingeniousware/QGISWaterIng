import json
import os
import resultTypes as rt
from epanet.toolkit import ENepanet
from epanet.util import EN


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

    try:
        
        enData = ENepanet()
        enData.ENopen(inpfile, rptfile, binfile)
        enData.ENsolveH()
        enData.ENsolveQ()
        try:
            enData.ENreport()
        except:
            pass
        
        nNodes = enData.ENgetcount(EN.NODECOUNT)
        
        valoresNodes = []
    
        #result["BASE DEMAND"] = 1
        #print(error)
        for i in range(1, nNodes):
            a = enData.ENgetnodevalue(i, EN.BASEDEMAND)
            b = enData.ENgetnodevalue(i, EN.DEMAND)
            c = enData.ENgetnodevalue(i, EN.PRESSURE)
            d = enData.ENgetnodevalue(i, EN.HEAD)
            valoresNodes.append(rt.ResultNode(a, b, c, d))
    
        # Paso 3: Escribe la lista en un archivo JSON
        jsonFile = file_prefix + "Node" + ".json"
        with open(jsonFile, 'w') as archivo_json:
            json.dump([item.to_dict() for item in valoresNodes], archivo_json, ensure_ascii = False, indent = 4)
        
        print("Cantidad de nodos: ", nNodes)
        nLinks = enData.ENgetcount(EN.LINKCOUNT)
        print("Cantidad de tuberias: ", nLinks)
        linkResult = []
        
        for i in range(1, nLinks):
            a = enData.ENgetlinkvalue(i, EN.LPS)
            b = enData.ENgetlinkvalue(i, EN.HEADLOSS)
            c = enData.ENgetlinkvalue(i, EN.STATUS)
            d = enData.ENgetlinkvalue(i, EN.DIAMETER)
            g = enData.ENgetlinkvalue(i, EN.MINORLOSS)
            linkResult.append(rt.ResultLink(a, b, c, d, g))
            
        # Paso 3: Escribe la lista en un archivo JSON
        jsonFile = file_prefix + "Link" + ".json"
        with open(jsonFile, 'w') as archivo_json:
            json.dump([item.to_json() for item in linkResult], archivo_json, ensure_ascii=False, indent=4)
            
        flows = enData.ENgetflowunits()
        if flows == 0: UndCaudal = "CFS"
        if flows == 1: UndCaudal = "GPM"
        if flows == 2: UndCaudal = "MGD"
        if flows == 3: UndCaudal = "IMGD"
        if flows == 4: UndCaudal = "AFD"
        if flows == 5: UndCaudal = "LPS"
        if flows == 6: UndCaudal = "LPM"
        if flows == 7: UndCaudal = "MLD"
        if flows == 8: UndCaudal = "CMH"
        if flows == 9: UndCaudal = "CMD"
        print("Unidad de caudal: ", UndCaudal)
        enData.ENclose()
    
    except Exception as e:
        raise e