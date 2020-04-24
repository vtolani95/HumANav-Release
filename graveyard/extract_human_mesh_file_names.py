import os
import pickle

base_dir = '/home/ext_drive/somilb/data/surreal/code/surreal/datageneration/visual_mpc_human_meshes_with_velocity_information_v3'

outfile = '/home/vtolani/Documents/Projects/HumANav/graveyard/expected_human_meshes.txt'

def extract_human_mesh_file_names():
    humanav_file_names = []

    velocity_dirs = os.listdir(base_dir)
    for velocity_dir in velocity_dirs:
        full_velocity_dir = os.path.join(base_dir, velocity_dir)
        if os.path.isdir(full_velocity_dir):
            pose_dirs = os.listdir(full_velocity_dir)
            for pose_dir in pose_dirs:
                full_pose_dir = os.path.join(full_velocity_dir, pose_dir)
                if os.path.isdir(full_pose_dir):
                    body_shape_dirs = os.listdir(full_pose_dir)
                    for body_shape_dir in body_shape_dirs:
                        full_body_shape_dir = os.path.join(full_pose_dir, body_shape_dir)
                        if os.path.isdir(full_body_shape_dir):
                            gender_dirs = os.listdir(full_body_shape_dir)
                            for gender_dir in gender_dirs:
                                full_gender_dir = os.path.join(full_body_shape_dir, gender_dir)
                                if os.path.isdir(full_gender_dir):
                                    human_files = os.listdir(full_gender_dir)
                                    human_mesh_files = [os.path.join(velocity_dir, pose_dir, body_shape_dir, gender_dir, x) for x in human_files if '.obj' in x]

                                    humanav_file_names.extend(human_mesh_files)
   
    with open(outfile, 'w') as f:
        humanav_file_names_string = '\n'.join(humanav_file_names)
        f.write(humanav_file_names_string)

if __name__ == '__main__':
    extract_human_mesh_file_names()

