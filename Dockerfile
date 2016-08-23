FROM debian

ENV build_dir /mnt/build

WORKDIR ${build_dir}

RUN apt-get clean && apt-get update && apt-get install -y \
    debhelper \
    devscripts \
    python3-all \
    python3-setuptools \
    python3-pytest

ENTRYPOINT ${build_dir}/debian/build_package.py
