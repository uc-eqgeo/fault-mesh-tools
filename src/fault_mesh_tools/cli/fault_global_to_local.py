#!/usr/bin/env python3
"""
Simple app to convert either a single VTK file or a directory with
multiple VTK files to local coordinates (best-fit plane) and then
output as a STL file, along with coordinate conversion metadata.
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
vtkSuffix = '.vtk'
vtkSearch = '*' + vtkSuffix
stlSuffix = '.stl'
mdSuffix = '.pkl'

# ----------------------------------------------------------------------
def convertFile(inFile, outRoot):
    """
    Function to read a VTK file and output a STL file in local coordinates,
    along with metadata (in a pickle file).
    """

    outStl = outRoot.with_suffix(stlSuffix)
    outMD = outRoot.with_suffix(mdSuffix)
    
    # Read VTK file.
    vtk = meshio.read(inFile)
    points = vtk.points
    cells = vtk.cells

    # Get best-fit plane through points and rotation matrix.
    (plane_normal, plane_origin) = meshops.fit_plane_to_points(points, eps=1.0e-5)
    rotation_matrix = meshops.get_fault_rotation_matrix(plane_normal, cutoff_vecmag=0.98)
    
    # Local coordinates.
    (points_local, edges_local, fault_is_plane) = meshops.fault_global_to_local(points, rotation_matrix, plane_origin)

    # Write coordinate info to pickle file.
    surface_info = {"plane_normal": plane_normal,
                    "plane_origin": plane_origin,
                    "fault_is_plane": fault_is_plane}
    f = open(outMD, "wb")
    pickle.dump(surface_info, f)
    f.close()

    # Write mesh as STL file.
    mesh = meshio.Mesh(points_local, cells)
    meshio.write(outStl, mesh)

    return
    

def convertDir(inPath, outPath, inQualifier, outQualifier):
    """
    Function to convert a directory of VTK files to STL files in local coordinates.
    """
    vtkFiles = sorted(inPath.glob(vtkSearch))
    for vtkFile in vtkFiles:
        inStem = vtkFile.stem
        outStem = inStem
        if (inQualifier):
            outStem = inStem.replace(inQualifier, outQualifier)
        elif (outQualifier):
            outStem = inStem + outQualifier
        outRoot = Path.joinpath(outPath, outStem)
        convertFile(vtkFile, outRoot)

    return

  
# ======================================================================
if __name__ == "__main__":

    # Get command-line arguments.
    parser = argparse.ArgumentParser(description='Convert one or more VTK files to STL files in local coordinates.')
    parser.add_argument("-i", "--in_files", action="store", 
                        dest="inFiles", required=True, help="input file or directory")
    parser.add_argument("-iq", "--in_qualifier", action="store", 
                        dest="inQualifier", default=None, help="additional input filename qualifier following unique string")
    parser.add_argument("-o", "--out_directory", action="store", 
                        dest="outDirectory", required=True, help="output directory")
    parser.add_argument("-oq", "--out_qualifier", action="store", 
                        dest="outQualifier", default="_local", help="additional output filename qualifier following unique string")

    args = parser.parse_args()

    inPath = Path(args.inFiles)
    outDir = Path(args.outDirectory)
    outDir.mkdir(parents=True, exist_ok=True)
    inQualifier = args.inQualifier
    outQualifier = args.outQualifier

    # Case 1:  Convert single file.
    if (inPath.is_file()):
        inSuff = inPath.suffix
        inStem = inPath.stem
        if (inSuff != vtkSuffix):
            msg = 'Only VTK (*.vtk) files are allowed as input.'
            raise ValueError(msg)
        outStem = inStem
        if (inQualifier):
            outStem = inStem.replace(inQualifier, outQualifier)
        elif (outQualifier):
            outStem = inStem + outQualifier
        outPath = Path.joinpath(outDir, outStem)
        convertFile(inPath, outPath)
    # Case 2:  Convert directory.
    elif (inPath.is_dir()):
        convertDir(inPath, outDir, inQualifier, outQualifier)
    # Case 3:  Give up.
    else:
        msg = 'Unable to find %s.' % inPath
        raise ValueError(msg)
    
