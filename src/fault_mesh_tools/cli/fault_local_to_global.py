#!/usr/bin/env python3
"""
Simple app to convert either a single STL file or a directory with
multiple STL files to global coordinates, given the plane normal
and origin of the local coordinate system. Output is a corresponding
STL file.
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
mdSuffix = '.pkl'
mdSearch = '*' + mdSuffix

# ----------------------------------------------------------------------
def convertFile(inStl, inMD, outFile):
    """
    Function to read a STL file in local coordinates,
    along with metadata (in a pickle file), and generate an output STL
    file in global coordinates.
    """

    # Read STL and metadata files.
    stl = meshio.read(inStl)
    points = stl.points
    cells = stl.cells

    # Get rotation matrix and origin.
    f = open(inMD, 'rb')
    pl = pickle.load(f)
    f.close()
    rotation_matrix = meshops.get_fault_rotation_matrix(pl['plane_normal'], cutoff_vecmag=0.98)

    # Global coordinates.
    (points_global, edges_global) = meshops.fault_local_to_global(points, rotation_matrix, pl['plane_origin'])

    # Write mesh as STL file.
    mesh = meshio.Mesh(points_global, cells)
    meshio.write(outFile, mesh)

    return
    

def convertDir(inPath, outPath, inQualifier, outQualifier):
    """
    Function to convert a directory of STL files to STL files in global coordinates.
    """
    inStl = sorted(inPath.glob(stlSearch))
    inMD = sorted(inPath.glob(mdSearch))
    if (len(inStl) != len(inMD)):
        msg = 'Number of input STL files does not match number of input metadata files.'
        raise ValueError(msg)
    for fileNum in range(len(inStl)):
        stlIn = inStl[fileNum]
        MDIn = inMD[fileNum]
        inStem = stlIn.stem
        outStem = inStem
        if (inQualifier):
            outStem = inStem.replace(inQualifier, outQualifier)
        elif (outQualifier):
            outStem = inStem + outQualifier
        outRoot = Path.joinpath(outPath, outStem)
        outFile = outRoot.with_suffix(stlSuffix)
        convertFile(stlIn, MDIn, outFile)

    return

  
# ======================================================================
if __name__ == "__main__":

    # Get command-line arguments.
    parser = argparse.ArgumentParser(description='Convert one or more STL files in local coordinates to global coordinates.')
    parser.add_argument("-i", "--in_root", action="store", 
                        dest="inRoot", required=True, help="input root filename or directory")
    parser.add_argument("-iq", "--in_qualifier", action="store", 
                        dest="inQualifier", default=None, help="additional input filename qualifier following unique string")
    parser.add_argument("-o", "--out_directory", action="store", 
                        dest="outDirectory", required=True, help="output directory")
    parser.add_argument("-oq", "--out_qualifier", action="store", 
                        dest="outQualifier", default="_global", help="additional output filename qualifier following unique string")

    args = parser.parse_args()

    inRoot = Path(args.inRoot)
    testPath = inRoot.with_suffix(stlSuffix)
    outDir = Path(args.outDirectory)
    outDir.mkdir(parents=True, exist_ok=True)
    inQualifier = args.inQualifier
    outQualifier = args.outQualifier

    # Case 1:  Convert single file.
    if (testPath.is_file()):
        inSuff = testPath.suffix
        inStem = testPath.stem
        inMD = inRoot.with_suffix(mdSuffix)
        if (inSuff != stlSuffix):
            msg = 'Only STL (*.stl) files are allowed as input.'
            raise ValueError(msg)
        outStem = inStem
        if (inQualifier):
            outStem = inStem.replace(inQualifier, outQualifier)
        elif (outQualifier):
            outStem = inStem + outQualifier
        outPath = Path.joinpath(outDir, outStem)
        outFile = outPath.with_suffix(stlSuffix)
        convertFile(testPath, inMD, outFile)
    # Case 2:  Convert directory.
    elif (inRoot.is_dir()):
        convertDir(inRoot, outDir, inQualifier, outQualifier)
    # Case 3:  Give up.
    else:
        msg = 'Unable to find %s.' % inPath
        raise ValueError(msg)
    
