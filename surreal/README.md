## Generate Human Walking Meshes From SURREAL

The HumANav dataset uses photorealistic textured meshes from the [SURREAL](https://www.di.ens.fr/willow/research/surreal/) dataset. Please follow the following setup instructions; #1 and #2 are copied directly from the [SURREAL GitHub page](https://github.com/gulvarol/surreal).

## 1. Download SURREAL dataset

In order to download SURREAL dataset, you need to accept the license terms. The links to license terms and download procedure are available here:

https://www.di.ens.fr/willow/research/surreal/data/

Once you receive the credentials to download the dataset, you will have a personal username and password. 

## 2. Create your own synthetic data
### 2.1. Preparation
#### 2.1.1. SMPL data

a) You need to download SMPL for MAYA from http://smpl.is.tue.mpg.de in order to run the synthetic data generation code. Once you agree on SMPL license terms and have access to downloads, you will have the following two files:

```
basicModel_f_lbs_10_207_0_v1.0.2.fbx
basicModel_m_lbs_10_207_0_v1.0.2.fbx
```

Place these two files under `datageneration/smpl_data` folder.

b) With the same credentials as with the SURREAL dataset, you can download the remaining necessary SMPL data and place it in `datageneration/smpl_data`.

``` 
./download_smpl_data.sh /path/to/smpl_data yourusername yourpassword
```


#### 2.1.3. Blender
You need to download [Blender](http://download.blender.org/release/) and install scipy package to run the first part of the code. The provided code was tested with [Blender2.78](http://download.blender.org/release/Blender2.78/blender-2.78a-linux-glibc211-x86_64.tar.bz2), which is shipped with its own python executable as well as distutils package. Therefore, it is sufficient to do the following:

``` 
# Install blender 2.78
wget http://download.blender.org/release/Blender2.78/blender-2.78a-linux-glibc211-x86_64.tar.bz2

# Un-TAR Blender
tar xjf blender-2.78a-linux-glibc211-x86_64.tar.bz2 

# Export the BLENDER_PATH
export BLENDER_PATH='/path/to/blender/blender-2.78-linux-glibc219-x86_64'

# Install pip
wget https://bootstrap.pypa.io/get-pip.py
$BLENDER_PATH/2.78/python/bin/python3.5m get-pip.py

# Make sure you have libglu1
sudo apt-get install libglu1

# Install scipy
$BLENDER_PATH/2.78/python/bin/python3.5m -m pip install scipy
```

Note: Installation of pip may fail in Blender 2.78a (this is a known issue)
If this happens Blender 2.79a should work. You can install it from here (and then repeat the above steps substituting 2.79a for 2.78).
```
wget https://download.blender.org/release/Blender2.79/blender-2.79a-linux-glibc219-x86_64.tar.bz2
```


## 3. Custom Instructions for HumANav Data Generation

### Make sure your data is organized correctly

### Edit the config file
In the directory /path/to/HumANav/surreal/code update the following line in config
```
smpl_data_folder   = '/path/to/HumANav/surreal/download/SURREAL/smpl_data'
```

### Test the installation
```
$BLENDER_PATH/blender -b -t 1 -P export_human_meshes.py -- --idx 2 --ishape 0 --stride 59 --gender female --body_shape 1000 --outdir test_human_mesh_generation
```
The test should create the following directory structure:
```
test_human_mesh_generation/
    - velocity_0.000_m_s/
    - velocity_0.200_m_s/
    - velocity_0.500_m_s/
        - pose_2_ishape_0_stride_59/
            - body_shape_1000/
                - female/ # (here i is in [1, 2, 3])
                    - human_centering_info_i.pkl
                    - human_mesh_i.mtl
                    - human_mesh_i.obj
    - velocity_0.600_m_s/
        - pose_2_ishape_0_stride_59/
            - body_shape_1000/
                - female/  # (here i is in [4, 5, 6, 7, 8, 18, 19])
                    - human_centering_info_i.pkl 
                    - human_mesh_i.mtl
                    - human_mesh_i.obj
```
The human_mesh_i.obj (mesh of the corresponding human body), and human_centering_info_i.pkl (information to canonically center and position each human) files will be used in the HumANav dataset.

### Generate the Human Mesh Models for HumANav
Note: Full data generation takes around ~4 hours & 11 GB of space.
```
sh generate_meshes.sh
```
Human meshes will be saved in /path/to/HumANav/surreal/code/human_meshes
