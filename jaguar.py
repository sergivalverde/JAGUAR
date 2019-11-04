#!/usr/bin/env python3

# --------------------------------------------------
# JAGUAR:
#
# Just FAst seGmentation, bUt fAsteR
#
# Sergi Valverde 2019
# Docker version
# --------------------------------------------------

import os
import argparse
import time
import docker
from pyfiglet import Figlet

CURRENT_FOLDER = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":

    # Parse input options
    parser = argparse.ArgumentParser(
        description="JAGUAR: Just FAst seGmentation, bUt fAsteR")
    parser.add_argument('--input_image',
                        action='store',
                        help='T1 nifti image to process (mandatory)')
    parser.add_argument('--out_dir',
                        action='store',
                        help='Output directory to store the results')
    parser.add_argument('--gpu',
                        action='store_true',
                        help='Use GPU for computing (default=false)')
    parser.add_argument('--gpu_number',
                        type=int,
                        default=0,
                        help='Select the GPU number to use (default=0)')
    parser.add_argument('--verbose',
                        action='store_true',
                        help='Verbose mode')
    parser.add_argument('--update',
                        action='store_true',
                        help='Update the Docker image')

    opt = parser.parse_args()
    OUT_DIR = opt.out_dir
    GPU_USE = opt.gpu
    GPU_NUMBER = opt.gpu_number
    VERBOSE = opt.verbose
    UPDATE = opt.update
    # MODEL_NAME = opt.model
    # MODEL_PATH = os.path.join(CURRENT_FOLDER, 'models', MODEL_NAME)

    # --------------------------------------------------
    # Docker image
    # - update docker image at init
    #
    # --------------------------------------------------
    client = docker.from_env()
    CONTAINER_IMAGE = 'sergivalverde/jaguar:latest'

    if UPDATE:
        print('Updating the Docker image')
        client.images.pull(CONTAINER_IMAGE)

    # --------------------------------------------------
    # SET PATHS
    # Convert input path into an absolute path
    #
    # DATA_FOLDER: abs path  where the T1-w lives
    # IMAGE_PATH: abs path to the T1-w image
    # --------------------------------------------------
    input_image = opt.input_image
    if str.find(input_image, '/') >= 0:
        if os.path.isabs(input_image):
            (im_path, im_name) = os.path.split(input_image)
            DATA_PATH = im_path
            IMAGE_PATH = im_name
        else:
            (im_path, im_name) = os.path.split(input_image)
            DATA_PATH = os.path.join(os.getcwd(), im_path)
            IMAGE_PATH = im_name
    else:
        DATA_PATH = os.getcwd()
        IMAGE_PATH = opt.input_image

    # --------------------------------------------------
    # Docker options
    # - docker container paths
    # - volumes to mount
    # - command
    # - runtime
    # --------------------------------------------------

    # docker user
    UID = str(os.getuid())
    DOCKER_USER = UID + ':1000'
    # docker container paths
    DOCKER_DATA_PATH = '/home/docker/data'
    # DOCKER_MODEL_PATH = '/home/docker/src/models'

    # volumes to mount
    VOLUMES = {DATA_PATH: {'bind': DOCKER_DATA_PATH, 'mode': 'rw'}}
    # MODEL_PATH: {'bind': DOCKER_MODEL_PATH, 'mode': 'rw'}}

    # Skull stripping command
    COMMAND = 'python /home/docker/src/run_fastnet.py' + \
        ' --input_image ' + os.path.join(DOCKER_DATA_PATH,
                                         IMAGE_PATH) + ' --out_dir ' + OUT_DIR

    # --------------------------------------------------
    # run the container
    #
    # The container is stored
    # --------------------------------------------------

    t = time.time()

    if VERBOSE:
        f = Figlet(font="slant")
        print("--------------------------------------------------")
        print(f.renderText("JAGUAR"))
        print("Just FAst seGmentation, bUt fAsteR")
        print("(c) Sergi Valverde, 2019")
        print(" ")
        print("version: v0.1 (Docker)")
        print("--------------------------------------------------")
        print(" ")
        print("Image information:")
        print("input path:", DATA_PATH)
        print("input image:", IMAGE_PATH)
        print("Output image:", OUT_DIR)
        print("Using GPU:", GPU_USE)
        print("--------------------------------------------------")

    if GPU_USE:
        GPU_OPTIONS = ' --gpu ' + ' --gpu_number ' + str(GPU_NUMBER)
        COMMAND += GPU_OPTIONS
        client.containers.run(image=CONTAINER_IMAGE,
                              command=COMMAND,
                              user=DOCKER_USER,
                              runtime='nvidia',
                              volumes=VOLUMES)
    else:
        client.containers.run(image=CONTAINER_IMAGE,
                              user=DOCKER_USER,
                              command=COMMAND,
                              volumes=VOLUMES)
    if VERBOSE:
        print('Computing time: %0.2f' % (time.time() - t))
