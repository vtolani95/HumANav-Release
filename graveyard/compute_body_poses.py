import os

base_dir = 'human_meshes'

def main():
    velocity_dirs = [os.path.join(base_dir, x) for x in os.listdir(base_dir)]
    pose_dirs = [] 
    for velocity_dir in velocity_dirs:
        if os.path.isdir(velocity_dir):
            pose_dirs.append([os.path.join(velocity_dir, x) for x in os.listdir(velocity_dir)])
    pose_dirs = [item for sublist in pose_dirs for item in sublist if 'DS_Store' not in item]
    body_shape_dirs = [os.listdir(x) for x in pose_dirs]
    body_shape_dirs = [item for sublist in body_shape_dirs for item in sublist if 'DS_Store' not in item]

    body_shapes = [int(x.split('body_shape_')[1]) for x in body_shape_dirs]
    print(set(body_shapes))
    print(len(set(body_shapes)))


if __name__ == '__main__':
    main()
