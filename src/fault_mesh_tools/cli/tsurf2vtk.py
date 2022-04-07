#!/usr/bin/env python3
"""
Simple app to convert either a single tsurf file or a directory with
multiple tsurf files to VTK format for visualization with Paraview or
other visualization packages.
"""

# The code requires numpy, meshio, pathlib,
# argparse and the fault_mesh_tools.faultmeshio package.
from pathlib import Path
import argparse
import sys
import numpy as np

import meshio

from fault_mesh_tools.faultmeshio import tsurf
# from rsqsim_api.io import tsurf

# File suffixes and search string.
tsurf_suffix = '.ts'
vtk_suffix = '.vtk'
tsurf_search = '*' + tsurf_suffix

# ----------------------------------------------------------------------
def convert_file(in_file, out_file):
    """
    Function to read a TSurf file and output a VTK file.
    """
    # Read TSurf file.
    tsurf_mesh = tsurf.tsurf(in_file)

    # Write mesh as VTK file.
    out_string = str(out_file)
    meshio.write(out_string, tsurf_mesh.mesh)

    return
    

def convert_dir(in_path, out_path, verbose):
    """
    Function to convert a directory of Tsurf files to VTK format.
    """
    tsurf_files = sorted(in_path.glob(tsurf_search))
    out_path.mkdir(parents=True, exist_ok=True)
    for tsurf_file in tsurf_files:
        stem = tsurf_file.stem
        if (verbose):
            print("Input file: %s" % stem)
        out_file = Path.joinpath(out_path, stem).with_suffix(vtk_suffix)
        convert_file(tsurf_file, out_file)

    return

  
# ======================================================================
if __name__ == "__main__":

    # Get command-line arguments.
    parser = argparse.ArgumentParser(description='Convert one or more TSurf files to VTK format.')
    parser.add_argument("-i", "--in_files", action="store", 
                        dest="in_files", required=True, help="input file or directory")
    parser.add_argument("-o", "--out_files", action="store", 
                        dest="out_files", required=True, help="output file or directory")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        dest="verbose", default=False, help="verbose output for directories")

    args = parser.parse_args()

    in_path = Path(args.in_files)
    out_path = Path(args.out_files)
    verbose = args.verbose

    # Case 1:  Convert single file.
    if (in_path.is_file()):
        in_suff = in_path.suffix
        in_stem = in_path.stem
        out_dir = out_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        if (in_suff != tsurf_suffix):
            msg = 'Only tsurf (*.ts) files are allowed as input.'
            raise ValueError(msg)
        out_path = out_path.with_suffix(vtk_suffix)
        convert_file(in_path, out_path)
    # Case 2:  Convert directory.
    elif (in_path.is_dir()):
        convert_dir(in_path, out_path, verbose)
    # Case 3:  Give up.
    else:
        msg = 'Unable to find %s.' % in_path
        raise ValueError(msg)
    
