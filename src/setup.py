from setuptools import setup, find_packages

setup(name='fault_mesh_tools',
      version='0.1',
      description='Tools for dealing with fault meshes and geometries',
      author='Charles Williams',
      author_email='c.williams@gns.cri.nz',
      packages=find_packages(),
      package_data={'fault_mesh_tools': ['data/*']},
      requires=[
          'numpy',
          'scipy',
          'shapely',
          'meshio',
          'rsqsim_api',
          'pathlib']
      )
