# Compose

Everything under compose directory will be mounted into the container.
Please modify the files as needed.

[podman-compose installation docs](https://github.com/containers/podman-compose#installation).

```shell
pip install podman-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
podman-compose up
```

or:

```shell
pip install docker-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
docker-compose up
docker-compose scale pulp_api=4 pulp_content=4
```
