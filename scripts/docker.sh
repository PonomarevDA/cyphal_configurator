#!/bin/bash

print_help() {
   echo "Wrapper under docker API for cyphal_tools.
It encapsulates all necessary docker flags and properly handles image versions.
https://github.com/PonomarevDA/kotleta_tools

usage: docker.sh [command]

Commands:
build                           Build docker image.
interactive                     Run container in interactive mode.
kill                            Kill all containers.
help                            Print this message and exit"
}

setup_image_name_and_version() {
    TAG_NAME=v0.4.0
    DOCKERHUB_REPOSITOTY=ponomarevda/cyphal_tools

    if uname -m | grep -q 'aarch64'; then
        TAG_NAME="$TAG_NAME""arm64"
    elif uname -m | grep -q 'x86_64'; then
        TAG_NAME="$TAG_NAME""amd64"
    else
        echo "unknown architecture"
        exit
    fi
    DOCKER_CONTAINER_NAME=$DOCKERHUB_REPOSITOTY:$TAG_NAME
}

setup_cyphal_config() {
    setup_image_name_and_version
    DOCKER_FLAGS="--net=host"
    DOCKER_FLAGS="$DOCKER_FLAGS -v "/tmp/.X11-unix:/tmp/.X11-unix:rw" -e DISPLAY=$DISPLAY -e QT_X11_NO_MITSHM=1)"
    source ./get_sniffer_symlink.sh
    CYPHAL_DEV_PATH_SYMLINK=$DEV_PATH_SYMLINK

    if [ ! -z $CYPHAL_DEV_PATH_SYMLINK ]; then
        DOCKER_FLAGS="$DOCKER_FLAGS --privileged -v $CYPHAL_DEV_PATH_SYMLINK:$CYPHAL_DEV_PATH_SYMLINK"
        DOCKER_FLAGS="$DOCKER_FLAGS -e CYPHAL_DEV_PATH_SYMLINK=$CYPHAL_DEV_PATH_SYMLINK"
    fi

    echo "Docker Cyphal settings:"
    echo "- DOCKER_CONTAINER_NAME is" $DOCKER_CONTAINER_NAME
    echo "- CYPHAL_DEV_PATH_SYMLINK is" $CYPHAL_DEV_PATH_SYMLINK
}

build_docker_image() {
    setup_image_name_and_version
    docker build -t $DOCKER_CONTAINER_NAME ..
}

run_interactive() {
    setup_cyphal_config
    docker container run --rm -it $DOCKER_FLAGS $DOCKER_CONTAINER_NAME /bin/bash
}

kill_all_containers() {
    docker kill $(docker ps -q)
}

cd "$(dirname "$0")"

if [ "$1" = "build" ]; then
    build_docker_image
elif [ "$1" = "interactive" ]; then
    run_interactive
elif [ "$1" = "kill" ]; then
    kill_all_containers
else
    print_help
fi
