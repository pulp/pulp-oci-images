# Build your own Pulp image

The Pulp images (`pulp/pulp` and `pulp/pulp-minimal`) come pre-installed with the set of plugins
we officially support. However, these images can be easily customized to suit your specific content
needs. 

## Change the versions of the plugins

The easiest way to customize the images is to specify the plugin versions that should be used when
building them. Clone and check out the `pulp-oci-images` repository to use the following commands.

```bash
# Using docker to build pulp/pulp with a custom pulpcore version
$ docker build --build-arg PULPCORE_VERSION="==3.65.0" --file images/pulp/Containerfile --tag pulp/pulp:custom
# Using buildah to build pulp/pulp-minimal & pulp-web with a custom pulp_gem version
$ buildah bud --build-arg PULP_GEM_VERSION=">=2.22.0" --file images/pulp-minimal/Containerfile.core --tag pulp/pulp-minimal:custom
$ buildah bud --build-arg FROM_TAG="custom" --file images/pulp-minimal/Containerfile.webserver --tag pulp/pulp-web:custom
```

## Add/remove plugins

If you want to build a custom image with a different set of plugins then the official images you are
going to need to write a custom Containerfile. The Containerfiles for `pulp` and `pulp-minimal` 
should be used as templates for creating your custom image. First clone and check out the 
`pulp-oci-images` repository. Then create a new directory in the `images/` directory for your 
custom image and copy over the corresponding Containerfile for the `pulp` or `pulp-minimal` image
into your new directory. See [Available Images](site:pulp-oci-images/docs/admin/reference/available-images/)
for more information on the difference between the two images.

### pulp image customization

Here is an example of a customized Containerfile for the multiprocess image.

```dockerfile title="custom/Containerfile"
ARG FROM_TAG="latest"
# The multiprocess pulp image must inherit from pulp/pulp-ci-centos9
# The tags follow pulpcore-versioning 3.Y(.Z), we recommend using "latest"
FROM pulp/pulp-ci-centos9:${FROM_TAG}

# These are extra pip requirements needed to run Pulp
COPY images/assets/requirements.extra.txt /requirements.extra.txt

# Here you customize the plugins and their versions that you want to install
RUN pip3 install --upgrade \
  pulpcore[s3,google,azure] \
  pulp-custom-plugin \
  -r /requirements.extra.txt \
  -c /constraints.txt && \
  rm -rf /root/.cache/pip

# collectstatic makes the api browsable in a web browser
USER pulp:pulp
RUN PULP_STATIC_ROOT=/var/lib/operator/static/ PULP_CONTENT_ORIGIN=localhost \
       /usr/local/bin/pulpcore-manager collectstatic --clear --noinput --link
USER root:root

# If you plugin has extra API routes you need to link them here into /etc/nginx/pulp/
RUN ln $(pip3 show pulp_custom_plugin | sed -n -e 's/Location: //p')/pulp_custom_plugin/app/webserver_snippets/nginx.conf /etc/nginx/pulp/pulp_custom_plugin.conf

# Add pulp-ui to the image, specified using a build-arg PULP_UI_URL 
ARG PULP_UI_URL
ENV PULP_UI=${PULP_UI_URL:-false}
RUN \
  if [ -n "$PULP_UI_URL" ]; then \
    mkdir -p "${PULP_STATIC_ROOT}pulp_ui"; \
    curl -Ls $PULP_UI_URL | tar -xzv -C "${PULP_STATIC_ROOT}pulp_ui"; \
  fi
```

Build your custom `pulp` image

```bash
# Run from the root of the pulp-oci-images/ repository
$ docker build --file images/custom/Containefile . --tag pulp/pulp:custom
```

### pulp-minimal customization

Here is an example of a customized Containerfile for the single-process image.

```dockerfile title="custom-minimal/Containerfile.core"
ARG FROM_TAG="latest"
# The single-process pulp-minimal image must inherit from pulp/base
# The tags follow pulpcore-versioning 3.Y(.Z), we recommend using "latest"
FROM pulp/base:${FROM_TAG}

COPY images/assets/requirements.extra.txt /requirements.extra.txt
COPY images/assets/requirements.minimal.txt /requirements.minimal.txt

# Here you customize the plugins and their versions that you want to install
RUN pip3 install --upgrade \
  pulpcore[s3,google,azure] \
  pulp-custom-plugin \
  -r /requirements.extra.txt \
  -r /requirements.minimal.txt \
  -c /constraints.txt && \
  rm -rf /root/.cache/pip

# Prevent pip-installed /usr/local/bin/pulp-content from getting run instead of
# our /usr/bin/pulp-content script.
RUN rm -f /usr/local/bin/pulp-content

# collectstatic makes the api browsable in a web browser
USER pulp:pulp
RUN PULP_STATIC_ROOT=/var/lib/operator/static/ PULP_CONTENT_ORIGIN=localhost \
       /usr/local/bin/pulpcore-manager collectstatic --clear --noinput --link
USER root:root

# Correct the permissions needed for Pulp folders
RUN chmod 2775 /var/lib/pulp/{scripts,media,tmp,assets}
RUN chown :root /var/lib/pulp/{scripts,media,tmp,assets}
```

### pulp-web customization

If you customize the `pulp-minimal` image you will also need to customize the `pulp-web` image.

```dockerfile title="custom-minimal/Containerfile.webserver"
ARG FROM_TAG="custom"
# The web image must inherit from your custom pulp-minimal image, if you rename
# the image then you should rename it here, else we recommend changing the 
# default FROM_TAG to your custom tag
FROM pulp/pulp-minimal:${FROM_TAG} as builder

# Necessary directories for the web image
RUN mkdir -p /etc/nginx/pulp \
             /www/data \

# Here you should link every plugin that offers extra API routes to the
# /etc/nginx/pulp/ directory
RUN ln $(pip3 show pulp_custom_plugin | sed -n -e 's/Location: //p')/pulp_custom_plugin/app/webserver_snippets/nginx.conf /etc/nginx/pulp/pulp_custom_plugin.conf

# The rest should be left untouched unless you want a different nginx image/configuration
FROM docker.io/centos/nginx-116-centos7:1.16

COPY --from=builder /etc/nginx/pulp/*.conf "${NGINX_DEFAULT_CONF_PATH}"/

# Run script uses standard ways to run the application
CMD nginx -g "daemon off;"
```

Afterwards you can build both images with these commands:

```bash
$ docker build --file images/custom-minimal/Containerfile.core . --tag pulp/pulp-minimal:custom
$ docker build --build-arg FROM_TAG="custom" --file images/custom-minimal/Containerfile.webserver --tag pulp/pulp-web:custom
```
