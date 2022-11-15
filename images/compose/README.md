# Compose

Everything under the assets directory will be mounted into the container.
Please modify the files as needed.

[podman-compose installation docs](https://github.com/containers/podman-compose#installation).

## Running with podman

```shell
pip install podman-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
podman-compose up
```

## Running with docker and scaling

```shell
pip install docker-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
docker-compose up
docker-compose scale pulp_api=4 pulp_content=4
```

## Running with podman and using existing directories for data
```shell
pip install podman-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
mkdir ../../pgsql ../../pulp_storage
podman unshare chown 700:700 ../../pulp_storage
podman-compose -f docker-compose.folders.yml up
```

## Running with docker and using existing directories for data
```shell
pip install podman-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
mkdir ../../pgsql ../../pulp_storage
sudo chown 700:700 ../../pulp_storage
podman-compose -f docker-compose.folders.yml up
```
