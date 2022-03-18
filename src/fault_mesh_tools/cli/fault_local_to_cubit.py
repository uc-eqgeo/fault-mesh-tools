#!/usr/bin/env python3
"""
Simple app to convert either a single STL file or a directory with
multiple STL files to cubit journal commands to generate a new mesh
with a different resolution. Output is a STL file.
"""

# The code requires numpy, pathlib, argparse, sys, pickle, meshio,
# and the fault_mesh_tools.meshops package.
import numpy

from pathlib import Path
import argparse
import sys
import pickle

import meshio

from fault_mesh_tools.meshops import meshops

# File suffixes and search string.
stlSuffix = '.stl'
stlSearch = '*' + stlSuffix
jouSuffix = '.jou'

# ----------------------------------------------------------------------
def convertFile(inStl, outStl, outJournal, resolution):
    """
    Function to generate Cubit journal commands to generate a mesh based
    on an input STL file.
    """

    # Open journal file and create commands.
    f = open(outJournal, 'w')
    f.write('import stl ' + '"' + str(inStl) + '"\n')
    f.write('surface all scheme trimesh\n')
    f.write('surface all size ' + resolution + '\n')
    f.write('mesh surface all\n')
    f.write('export stl ' + '"' + str(outStl) + '" overwrite\n')
    f.close()
    
    return
    

def convertDir(inPath, outPath, inQualifier, outQualifier, resolution):
    """
    Function to convert a directory of STL files to Cubit journal commands.
    """
    inStl = sorted(inPath.glob(stlSearch))
    for fileNum in range(len(inStl)):
        stlIn = inStl[fileNum]
        inStem = stlIn.stem
        outStem = inStem
        if (inQualifier):
            outStem = inStem.replace(inQualifier, outQualifier)
        elif (outQualifier):
            outStem = inStem + outQualifier
        outRoot = Path.joinpath(outPath, outStem)
        outJournal = outRoot.with_suffix(jouSuffix)
        outStl = outRoot.with_suffix(stlSuffix)
        convertFile(stlIn, outStl, outJournal, resolution)

    return

  
# ======================================================================
if __name__ == "__main__":

    # Get command-line arguments.
    parser = argparse.ArgumentParser(description='Generate Cubit commands to a new mesh based on input STL files.')
    parser.add_argument("-i", "--in_root", action="store", 
                        dest="inRoot", required=True, help="input root filename or directory")
    parser.add_argument("-iq", "--in_qualifier", action="store", 
                        dest="inQualifier", default=None, help="additional input filename qualifier following unique string")
    parser.add_argument("-o", "--out_directory", action="store", 
                        dest="outDirectory", required=True, help="output directory")
    parser.add_argument("-oq", "--out_qualifier", action="store", 
                        dest="outQualifier", default="_global", help="additional output filename qualifier following unique string")
    parser.add_argument("-r", "--resolution", action="store", 
                        dest="resolution", default=2000.0, help="resolution of new mesh from Cubit in meters")

    args = parser.parse_args()

    inRoot = Path(args.inRoot).resolve()
    testPath = inRoot.with_suffix(stlSuffix)
    outDir = Path(args.outDirectory).resolve()
    outDir.mkdir(parents=True, exist_ok=True)
    inQualifier = args.inQualifier
    outQualifier = args.outQualifier
    resolution = args.resolution

    # Case 1:  Convert single file.
    if (testPath.is_file()):
        inSuff = testPath.suffix
        inStem = testPath.stem
        if (inSuff != stlSuffix):
            msg = 'Only STL (*.stl) files are allowed as input.'
            raise ValueError(msg)
        outStem = inStem
        if (inQualifier):
            outStem = inStem.replace(inQualifier, outQualifier)
        elif (outQualifier):
            outStem = inStem + outQualifier
        outPath = Path.joinpath(outDir, outStem)
        outStl = outPath.with_suffix(stlSuffix)
        outJou = outPath.with_suffix(jouSuffix)
        convertFile(testPath, outStl, outJou, resolution)
    # Case 2:  Convert directory.
    elif (inRoot.is_dir()):
        convertDir(inRoot, outDir, inQualifier, outQualifier, resolution)
    # Case 3:  Give up.
    else:
        msg = 'Unable to find %s.' % inPath
        raise ValueError(msg)
    
