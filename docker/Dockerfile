
FROM ubuntu:22.04
LABEL description="Cyphal tools"
SHELL ["/bin/bash", "-c"]
WORKDIR cyphal_configurator

# 1. Install basic requirements
RUN apt-get update && apt-get upgrade -y

# 2. Install requirements
COPY scripts/ubuntu_22_04.sh scripts/ubuntu_22_04.sh
RUN ./scripts/ubuntu_22_04.sh

# 5. Copy files
COPY scripts/ scripts/
COPY config/ config/
COPY public_regulated_data_types/ public_regulated_data_types/


CMD echo "main process has been started"                                        &&  \
    echo "container has been finished"