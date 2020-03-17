from setuptools import setup
from setuptools import find_packages

setup(name='humanav',
  version='0.0.1',
  author='Varun Tolani',
  author_email='vtolani@eecs.berkeley.edu',
  description='Human Active Navigation Dataset',
  packages=find_packages(),
  license='UC Berkeley',
  install_requires=[]
#install_requires=['PyOpenGL', 'pyopengl-accelerate', 'numpy',
  #  'opencv-python', 'pyassimp', 'pytest', 'ipython', 'scikit-image',
  #  'yattag']
)
