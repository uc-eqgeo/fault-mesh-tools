#!/usr/bin/env python3
"""
Simple app to convert either a single VTK file or a directory with
multiple VTK files to local coordinates (best-fit plane) and then
output as a STL file, along with coordinate conversion metadata.
"""

# The code requires numpy, pathlib, argparse, sys, pickle, meshio,
# and the fault_mesh_tools.meshops package.
import numpy as np

from pathlib import Path
import argparse
import sys
import pickle

import meshio

from fault_mesh_tools.meshops import meshops

# File suffixes and search string.
vtk_suffix = '.vtk'
vtk_search = '*' + vtk_suffix
stl_suffix = '.stl'
md_suffix = '.pkl'

# ----------------------------------------------------------------------
def convert_file(in_file, out_root):
    """
    Function to read a VTK file and output a STL file in local coordinates,
    along with metadata (in a pickle file).
    """

    out_stl = out_root.with_suffix(stl_suffix)
    out_md = out_root.with_suffix(md_suffix)
    
    # Read VTK file.
    vtk = meshio.read(in_file)
    points = vtk.points
    cells = vtk.cells

    # Get best-fit plane through points and rotation matrix.
    (plane_normal, plane_origin) = meshops.fit_plane_to_points(points, eps=1.0e-5)
    rotation_matrix = meshops.get_fault_rotation_matrix(plane_normal, cutoff_vecmag=0.98)
    (rotation_axis, rotation_angle) = meshops.axis_angle_from_rotation_matrix(rotation_matrix)
    
    # Local coordinates.
    (points_local, edges_local, fault_is_plane) = meshops.fault_global_to_local(points, rotation_matrix, plane_origin)

    # Write coordinate info to pickle file.
    surface_info = {"plane_normal": plane_normal,
                    "plane_origin": plane_origin,
                    "rotation_axis": rotation_axis,
                    "rotation_angle": rotation_angle,
                    "fault_is_plane": fault_is_plane}
    f = open(out_md, "wb")
    pickle.dump(surface_info, f)
    f.close()

    # Write mesh as STL file.
    mesh = meshio.Mesh(points_local, cells)
    meshio.write(out_stl, mesh)

    return
    

def convert_dir(in_path, out_path, in_qualifier, out_qualifier, verbose):
    """
    Function to convert a directory of VTK files to STL files in local coordinates.
    """
    vtk_files = sorted(in_path.glob(vtk_search))
    for vtk_file in vtk_files:
        in_stem = vtk_file.stem
        out_stem = in_stem
        if (verbose):
            print("Input file:  %s" % in_stem)
        if (in_qualifier):
            out_stem = in_stem.replace(in_qualifier, out_qualifier)
        elif (out_qualifier):
            out_stem = in_stem + out_qualifier
        out_root = Path.joinpath(out_path, out_stem)
        convert_file(vtk_file, out_root)

    return

  
# ======================================================================
if __name__ == "__main__":

    # Get command-line arguments.
    parser = argparse.ArgumentParser(description='Convert one or more VTK files to STL files in local coordinates.')
    parser.add_argument("-i", "--in_files", action="store", 
                        dest="in_files", required=True, help="input file or directory")
    parser.add_argument("-iq", "--in_qualifier", action="store", 
                        dest="in_qualifier", default=None, help="additional input filename qualifier following unique string")
    parser.add_argument("-o", "--out_directory", action="store", 
                        dest="out_directory", required=True, help="output directory")
    parser.add_argument("-oq", "--out_qualifier", action="store", 
                        dest="out_qualifier", default="_local", help="additional output filename qualifier following unique string")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        dest="verbose", default=False, help="verbose output for directories")

    args = parser.parse_args()

    in_path = Path(args.in_files)
    out_dir = Path(args.out_directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    in_qualifier = args.in_qualifier
    out_qualifier = args.out_qualifier
    verbose = args.verbose

    # Case 1:  Convert single file.
    if (in_path.is_file()):
        in_suff = in_path.suffix
        in_stem = in_path.stem
        if (in_suff != vtk_suffix):
            msg = 'Only VTK (*.vtk) files are allowed as input.'
            raise ValueError(msg)
        out_stem = in_stem
        if (in_qualifier):
            out_stem = in_stem.replace(in_qualifier, out_qualifier)
        elif (out_qualifier):
            out_stem = in_stem + out_qualifier
        out_path = Path.joinpath(out_dir, out_stem)
        convert_file(in_path, out_path)
    # Case 2:  Convert directory.
    elif (in_path.is_dir()):
        convert_dir(in_path, out_dir, in_qualifier, out_qualifier, verbose)
    # Case 3:  Give up.
    else:
        msg = 'Unable to find %s.' % in_path
        raise ValueError(msg)
    
