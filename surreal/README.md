## Generate Human Walking Meshes From SURREAL

The HumANav dataset uses photorealistic textured meshes from the [SURREAL](https://www.di.ens.fr/willow/research/surreal/) dataset. Please follow the following setup instructions; #1 and #2 are copied directly from the [SURREAL GitHub page](https://github.com/gulvarol/surreal).

## 1. Download SURREAL dataset

In order to download SURREAL dataset, you need to accept the license terms. The links to license terms and download procedure are available here:

https://www.di.ens.fr/willow/research/surreal/data/

Once you receive the credentials to download the dataset, you will have a personal username and password. Use these either to download the dataset excluding optical flow data from [here: (SURREAL_v1.tar.gz, 86GB)](https://lsh.paris.inria.fr/SURREAL/SURREAL_v1.tar.gz) or download individual files with the `download/download_surreal.sh` script as follows:

``` shell
./download_surreal.sh /path/to/dataset yourusername yourpassword
```


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

``` shell
# Install pip
/blenderpath/2.78/python/bin/python3.5m get-pip.py
# Install scipy
/blenderpath/2.78/python/bin/python3.5m pip install scipy
```

`get-pip.py` is downloaded from [pip](https://pip.pypa.io/en/stable/installing/). Replace the `blenderpath` with your own and set `BLENDER_PATH`.

*Known problem: Blender2.78a has problems with pip. You can try with new versions of Blender. Otherwise, you can install the dependencies such as `scipy` to a new python3.5 environment and add this environment's `site-packages` to `PYTHONPATH` before running Blender.*

## 3. Custom Instructions for HumANav Data Generation

##### Export the Blender path
```
export BLENDER_PATH='/home/ext_drive/somilb/data/surreal/blender-2.78-linux-glibc219-x86_64'
```


### Test the installation
```
TODO: put something here
```

### Generate the Human Mesh Models for HumANav
Note: Full data generation may take a few hours. 
```
sh generate_meshes.sh
```

