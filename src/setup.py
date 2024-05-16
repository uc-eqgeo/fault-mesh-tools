from setuptools import setup, find_packages

setup(name='fault_mesh_tools',
      version='0.1',
      description='Tools for dealing with fault meshes and geometries',
      author='Charles Williams',
      author_email='c.williams@gns.cri.nz',
      packages=find_packages(),
      package_data={'fault_mesh_tools': ['data/*']},
      scripts=['fault_mesh_tools/cli/fmt_fault_global_to_local',
               'fault_mesh_tools/cli/fmt_fault_local_to_global',
               'fault_mesh_tools/cli/fmt_ts_fault_local_to_cubit',
               'fault_mesh_tools/cli/fmt_ts_fault_local_to_cubit_nurbs',
               'fault_mesh_tools/cli/fmt_tsurf2vtk'],
      requires=[
          'numpy',
          'scipy',
          'shapely',
          'meshio',
          'rsqsim_api',
          'pathlib',
          'argparse',
          'pickle',
          'sys',
          'six',
          'os']
      )
