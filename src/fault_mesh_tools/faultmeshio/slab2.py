import numpy as np
import pygmt as pg
import meshio

def read_slab2(in_file):
    """
    Read slab2 .grd file.
    """
    gmt = pg.load_dataarray(in_file)
    x_in = gmt.x
    y_in = gmt.y
    vals_in = gmt.values
    x_pos_east = False
    y_pos_north = False
    if (x_in[1] > x_in[0]):
        x_pos_east = True
    if (y_in[1] > y_in[0]):
        y_pos_north = True

    return (x_in, y_in, vals_in, x_pos_east, y_pos_north)


def write_slab2_outline(points, out_file):
    """
    Write contour defining slab2 fault as a .vtk file.
    """
    mesh = meshio.Mesh(points, cells=[])
    meshio.write(out_file, mesh)

    return
