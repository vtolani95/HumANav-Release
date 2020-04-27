# HumANav
Welcome to the Human Active Navigation Dataset (HumANav), a codebase for photorealistic simulations of humans in indoor office environments! We are a team of researchers from UC Berkeley and Google Brain.

We release this codebase as a part of ["Visual Navigation Among Humans with Optimal Control as a Supervisor"](https://arxiv.org/pdf/2003.09354.pdf). In this work we show that HumANav enables zero-shot transfer of learning based navigation algorithms directly from simulation to reality. Code for the navigation algorithms can be found HERE. We hope that HumANav can be a useful tool for the broader visual navigation, computer vision, and robotics communities.

For rendering purposes, we use the [Swiftshader](https://github.com/google/swiftshader) rendering engine, a CPU based rendering
engine for photorealistic visuals (rgb, disparity, surface normal, etc.) from textured meshes used in. We use mesh scans of office buildings from the [Stanford Large Scale 3d Indoor Spaces Dataset (SD3DIS)](http://buildingparser.stanford.edu/dataset.html) , however the rendering engine is independent of the meshes used. In principle, textured meshes from scans of any office buildings can be used. For human meshes we turn to the [SURREAL Dataset](https://www.di.ens.fr/willow/research/surreal/data/) which renders images of synthetic humans in a variety of poses, genders, body shapes, and lighting conditions. Though the meshes themselves are synthetic, the human poses in the SURREAL dataset come from real human motion capture data and contain a variety of actions including running, jumping, dancing, acrobatics, and walking. We focus on the subset of poses in which the human is walking.

## Data

#### Render the Human Meshes
Follow the instructions in surreal/README.md.

#### Download SD3DIS data
Follow the instructions in sd3dis/README.md

### Configure HumANav to look for your data.
HumANav is independent of the actual indoor office environment and human meshes used. In this work we use human meshes exported from the SURREAL dataset and scans of indoor office environments from the S3DIS dataset. However, if you would like to use other meshes, please download and configure them yourself and update the parameters below to point to your data installation.

In ./humanav/renderer_params.py change the following lines
```
def get_traversible_dir():
    return '/PATH/TO/HumANav/sd3dis/stanford_building_parser_dataset/traversibles'

def get_sbpd_data_dir():
    return '/PATH/TO/HumANav/sd3dis/stanford_building_parser_dataset/'

def get_surreal_mesh_dir():
    return '/PATH/TO/HumANav/surreal/code/human_meshes'

def get_surreal_texture_dir():
    return '/PATH/TO/HumANav/surreal/code/human_textures'
```

## Setup
### Install Anaconda, gcc, g++
```
# Install Anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2019.07-Linux-x86_64.sh
bash Anaconda3-2019.07-Linux-x86_64.sh

# Install gcc and g++ if you don't already have them
sudo apt-get install gcc
sudo apt-get install g++
```

### Setup A Virtual Environment
```
TODO: Add an environment.yml file & change the name to humanav
conda env create -f environment.yml
conda activate humanav
```

#### Patch the OpenGL Installation
In the terminal from the root directory of the project run the following commands.
```
1. cd mp_env
2. bash patches/apply_patches_3.sh
```
If the script fails there are instructions in apply_patches_3.sh describing how to manually apply the patch.

#### Install Libassimp-dev
In the terminal run:
```
sudo apt-get install libassimp-dev
```


## Citing This Work
TODO: CHANGE THIS
If you use the WayPtNav simulator or algorithms in your research please cite:
```
@article{bansal2019-lb-wayptnav,
  title={Combining Optimal Control and Learning for Visual Navigation in Novel Environments},
  author={Somil Bansal and Varun Tolani and Saurabh Gupta and Jitendra Malik and Claire Tomlin},
  booktitle={3rd Annual Conference on Robot Learning (CoRL)},  
  year={2019}
}
```
