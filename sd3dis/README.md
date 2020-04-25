We follow the method outlined in ["Cognitive Mapping and Planning for Visual Navigation"](https://github.com/tensorflow/models/tree/master/research/cognitive_mapping_and_planning) to download the SD3DIS data. Please follow the steps below

### Download and preprocess the meshes

1.  Download the data from the [dataset website](http://buildingparser.stanford.edu/dataset.html).
    1.  [Raw meshes](https://goo.gl/forms/2YSPaO2UKmn5Td5m2). We need the meshes
        which are in the noXYZ folder. Download the tar files and place them in
        the `stanford_building_parser_dataset_raw` folder. For our example you need to   		 download `area_1_noXYZ.tar`. If you'd like you can also download the other areas which include `area_3_noXYZ.tar`, `area_5a_noXYZ.tar`,
        `area_5b_noXYZ.tar`, `area_6_noXYZ.tar`,
        `area_4_noXYZ.tar`.

2.  Preprocess the data.
    1.  Extract meshes using `preprocess_meshes_S3DIS.sh`. After
        this `ls data/stanford_building_parser_dataset/mesh` should have 6
        folders `area1`, `area3`, `area4`, `area5a`, `area5b`, `area6`, with
        textures and obj files within each directory.


### Download custom data from Google Drive (~TBD GB).
To run our code you will need to download data from google drive which includes precomputed traversible maps for building in the S3DIS dataset.
```
# To download the data via the command line run the following
pip install gdown
TODO: CHANGE THIS LINK
gdown https://drive.google.com/uc?id=1wpQMm_pfNgPAUduLjUggTSBs6psavJSK

# To download the data via your browser visit the following url
TODO: CHANGE THIS LINK
https://drive.google.com/file/d/1wpQMm_pfNgPAUduLjUggTSBs6psavJSK/view?usp=sharing

# Unzip the file LB_WayPtNav_Data.tar.gz
TODO: CHANGE THIS LINK
tar -zxf LB_WayPtNav_Data.tar.gz -C DESIRED_OUTPUT_DIRECTORY
```
