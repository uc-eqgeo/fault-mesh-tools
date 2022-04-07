#!/usr/bin/env python3
"""
Simple app to convert either a single STL file or a directory with
multiple STL files to global coordinates, given the plane normal
and origin of the local coordinate system. Output is a corresponding
STL file.
"""

# The code requires numpy, pathlib, argparse, sys, pickle, meshio,
# and the fault_mesh_tools.faultmeshops package.
import numpy as np

from pathlib import Path
import argparse
import sys
import pickle

import meshio

from fault_mesh_tools.faultmeshops import faultmeshops

# File suffixes and search string.
stl_suffix = '.stl'
stl_search = '*' + stl_suffix
md_suffix = '.pkl'
md_search = '*' + md_suffix

# ----------------------------------------------------------------------
def convert_file(in_stl, in_md, out_file):
    """
    Function to read a STL file in local coordinates,
    along with metadata (in a pickle file), and generate an output STL
    file in global coordinates.
    """

    # Read STL and metadata files.
    stl = meshio.read(in_stl)
    points = stl.points
    cells = stl.cells

    # Get rotation matrix and origin.
    f = open(in_md, 'rb')
    pl = pickle.load(f)
    f.close()
    rotation_matrix = faultmeshops.get_fault_rotation_matrix(pl['plane_normal'], cutoff_vecmag=0.98)

    # Global coordinates.
    (points_global, edges_global) = faultmeshops.fault_local_to_global(points, rotation_matrix, pl['plane_origin'])

    # Write mesh as STL file.
    mesh = meshio.Mesh(points_global, cells)
    meshio.write(out_file, mesh)

    return
    

def convert_dir(in_path, out_path, in_qualifier, out_qualifier, verbose):
    """
    Function to convert a directory of STL files to STL files in global coordinates.
    """
    in_stl = sorted(in_path.glob(stl_search))
    in_md = sorted(in_path.glob(md_search))
    if (len(in_stl) != len(in_md)):
        msg = 'Number of input STL files does not match number of input metadata files.'
        raise ValueError(msg)
    for file_num in range(len(in_stl)):
        stl_in = in_stl[file_num]
        md_in = in_md[file_num]
        in_stem = stl_in.stem
        out_stem = in_stem
        if (verbose):
            print("Input file:  %s" % in_stem)
        if (in_qualifier):
            out_stem = in_stem.replace(in_qualifier, out_qualifier)
        elif (out_qualifier):
            out_stem = in_stem + out_qualifier
        out_root = Path.joinpath(out_path, out_stem)
        out_file = out_root.with_suffix(stl_suffix)
        convert_file(stl_in, md_in, out_file)

    return

  
# ======================================================================
if __name__ == "__main__":

    # Get command-line arguments.
    parser = argparse.ArgumentParser(description='Convert one or more STL files in local coordinates to global coordinates.')
    parser.add_argument("-i", "--in_root", action="store", 
                        dest="inRoot", required=True, help="input root filename or directory")
    parser.add_argument("-iq", "--in_qualifier", action="store", 
                        dest="in_qualifier", default=None, help="additional input filename qualifier following unique string")
    parser.add_argument("-o", "--out_directory", action="store", 
                        dest="out_directory", required=True, help="output directory")
    parser.add_argument("-oq", "--out_qualifier", action="store", 
                        dest="out_qualifier", default="_global", help="additional output filename qualifier following unique string")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        dest="verbose", default=False, help="verbose output for directories")

    args = parser.parse_args()

    inRoot = Path(args.inRoot)
    testPath = inRoot.with_suffix(stl_suffix)
    outDir = Path(args.out_directory)
    outDir.mkdir(parents=True, exist_ok=True)
    in_qualifier = args.in_qualifier
    out_qualifier = args.out_qualifier
    verbose = args.verbose

    # Case 1:  Convert single file.
    if (testPath.is_file()):
        inSuff = testPath.suffix
        in_stem = testPath.stem
        in_md = inRoot.with_suffix(md_suffix)
        if (inSuff != stl_suffix):
            msg = 'Only STL (*.stl) files are allowed as input.'
            raise ValueError(msg)
        out_stem = in_stem
        if (in_qualifier):
            out_stem = in_stem.replace(in_qualifier, out_qualifier)
        elif (out_qualifier):
            out_stem = in_stem + out_qualifier
        out_path = Path.joinpath(outDir, out_stem)
        out_file = out_path.with_suffix(stl_suffix)
        convert_file(testPath, in_md, out_file)
    # Case 2:  Convert directory.
    elif (inRoot.is_dir()):
        convert_dir(inRoot, outDir, in_qualifier, out_qualifier, verbose)
    # Case 3:  Give up.
    else:
        msg = 'Unable to find %s.' % in_path
        raise ValueError(msg)
    
