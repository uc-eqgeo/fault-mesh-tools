#!/usr/bin/env python3
"""
Simple app to convert either a single STL file or a directory with
multiple STL files to cubit journal commands to generate a new mesh
with a different resolution. Output is a STL file.
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
jou_suffix = '.jou'
jou_master = 'master_local_to_cubit.jou'

# ----------------------------------------------------------------------
def convert_file(in_stl, in_md, out_stl, out_journal, resolution, smoothing, output_global):
    """
    Function to generate Cubit journal commands to generate a mesh based
    on an input STL file.
    """

    # Open journal file and create commands.
    f = open(out_journal, 'w')
    f.write('reset\n')
    f.write('import stl ' + '"' + str(in_stl) + '"\n')
    f.write('surface all scheme triadvance\n')
    f.write('surface all size ' + resolution + '\n')
    f.write('mesh surface all\n')
    if (smoothing):
        f.write('surface all smooth scheme condition number beta %s cpu 2\n' % smoothing)
        f.write('smooth surface all\n')
    if (output_global):
        m = open(in_md, 'rb')
        mv = pickle.load(m)
        m.close()
        ang_radians = mv['rotation_angle']
        axis = mv['rotation_axis']
        ang_degrees = -np.degrees(ang_radians)
        plane_origin = mv['plane_origin']
        f.write('rotate surface all about %g %g %g angle %g\n' % (axis[0], axis[1], axis[2], ang_degrees))
        f.write('volume all move x %g y %g z %g\n' % (plane_origin[0], plane_origin[1], plane_origin[2]))

    f.write('export stl ' + '"' + str(out_stl) + '" tri all mesh overwrite\n')
    f.close()
    
    return
    

def convert_dir(in_path, out_path, in_qualifier, out_qualifier, resolution, smoothing, output_global, verbose):
    """
    Function to convert a directory of STL files to Cubit journal commands.
    """
    in_stl = sorted(in_path.glob(stl_search))
    in_md = sorted(in_path.glob(md_search))
    if (len(in_stl) != len(in_md)):
        msg = 'Number of input STL files does not match number of input metadata files.'
        raise ValueError(msg)
    out_master = Path.joinpath(out_path, jou_master)
    m = open(out_master, 'w')
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
        out_journal = out_root.with_suffix(jou_suffix)
        out_stl = out_root.with_suffix(stl_suffix)
        m.write('playback "'"%s"'"\n' % out_journal)
        convert_file(stl_in, md_in, out_stl, out_journal, resolution, smoothing, output_global)

    m.close()
    return

  
# ======================================================================
if __name__ == "__main__":

    # Get command-line arguments.
    parser = argparse.ArgumentParser(description='Generate Cubit commands to a new mesh based on input STL files.')
    parser.add_argument("-i", "--in_root", action="store", 
                        dest="in_root", required=True, help="input root filename or directory")
    parser.add_argument("-iq", "--in_qualifier", action="store", 
                        dest="in_qualifier", default=None, help="additional input filename qualifier following unique string")
    parser.add_argument("-o", "--out_directory", action="store", 
                        dest="out_directory", required=True, help="output directory")
    parser.add_argument("-oq", "--out_qualifier", action="store", 
                        dest="out_qualifier", default="_global", help="additional output filename qualifier following unique string")
    parser.add_argument("-r", "--resolution", action="store", 
                        dest="resolution", default=2000.0, help="resolution of new mesh from Cubit in meters")
    parser.add_argument("-s", "--smoothing", action="store", 
                        dest="smoothing", default=None, help="condition number smoothing target for mesh")
    parser.add_argument("-og", "--output_global", action="store_true", 
                        dest="output_global", default=False, help="output mesh in global coordinates")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        dest="verbose", default=False, help="verbose output for directories")
     
    args = parser.parse_args()

    in_root = Path(args.in_root).resolve()
    test_path = in_root.with_suffix(stl_suffix)
    out_dir = Path(args.out_directory).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    in_qualifier = args.in_qualifier
    out_qualifier = args.out_qualifier
    resolution = args.resolution
    smoothing = args.smoothing
    output_global = args.output_global
    verbose = args.verbose

    # Case 1:  Convert single file.
    if (test_path.is_file()):
        in_suff = test_path.suffix
        in_stem = test_path.stem
        in_md = in_root.with_suffix(md_suffix)
        if (in_suff != stl_suffix):
            msg = 'Only STL (*.stl) files are allowed as input.'
            raise ValueError(msg)
        out_stem = in_stem
        if (in_qualifier):
            out_stem = in_stem.replace(in_qualifier, out_qualifier)
        elif (out_qualifier):
            out_stem = in_stem + out_qualifier
        out_path = Path.joinpath(out_dir, out_stem)
        out_stl = out_path.with_suffix(stl_suffix)
        out_jou = out_path.with_suffix(jou_suffix)
        convert_file(test_path, in_md, out_stl, out_jou, resolution, smoothing, output_global)
    # Case 2:  Convert directory.
    elif (in_root.is_dir()):
        convert_dir(in_root, out_dir, in_qualifier, out_qualifier, resolution, smoothing, output_global, verbose)
    # Case 3:  Give up.
    else:
        msg = 'Unable to find %s.' % in_path
        raise ValueError(msg)
    
