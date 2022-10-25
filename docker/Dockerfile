ARG ROS_DISTRO=noetic

FROM ros:$ROS_DISTRO
LABEL description="Cyphal tools"
SHELL ["/bin/bash", "-c"]
WORKDIR /catkin_ws/src/cyphal_tools 

# 1. Install basic requirements
RUN apt-get update && apt-get upgrade -y && apt-get install -y git ros-$ROS_DISTRO-catkin python3-pip python3-catkin-tools
RUN if [[ "$ROS_DISTRO" = "melodic" ]] ; then apt-get install -y python-pip python-catkin-tools ; fi

# 2. Install requirements
COPY scripts/install.sh scripts/install.sh
RUN ./scripts/install.sh

# 5. Copy files
COPY scripts/ scripts/
COPY config/ config/
COPY public_regulated_data_types/ public_regulated_data_types/


CMD echo "main process has been started"                                        &&  \
    echo "container has been finished"