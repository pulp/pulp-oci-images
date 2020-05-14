FROM fedora:31
ADD https://github.com/just-containers/s6-overlay/releases/download/v1.22.1.0/s6-overlay-amd64.tar.gz /tmp/
RUN tar xzf /tmp/s6-overlay-amd64.tar.gz -C /

# https://superuser.com/questions/959380/how-do-i-install-generate-all-locales-on-fedora
# This may not be necessary anymore because Fedora 30, unlike CentOS 7, has
# glibc subpackages like glibc-langpack-en.
RUN rm /etc/rpm/macros.image-language-conf
RUN echo 'LANG="en_US.UTF-8"' > /etc/locale.conf
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV PYTHONUNBUFFERED=0
ENV DJANGO_SETTINGS_MODULE=pulpcore.app.settings
ENV PULP_SETTINGS=/etc/pulp/settings.py
ENV _BUILDAH_STARTED_IN_USERNS=""
ENV BUILDAH_ISOLATION=chroot

# The Fedora 30 image already has tsflags=nodocs set in dnf.conf
# It already has pip
#
# wget & git are presumably needed for purposes like pip installs from git
#
# libxcrypt-compat is needed by psycopg2-binary from PyPI
#
# python3-psycopg2 is installed by ansible-pulp
#
# glibc-langpack-en is needed to provide the en_US.UTF-8 locale, which Pulp
# seems to need.
#
# python3-createrepo_c is needed for pulp_rpm
RUN		dnf -y update && \
		dnf -y install wget git && \
		dnf -y install libxcrypt-compat && \
		dnf -y install python3-psycopg2 && \
		dnf -y install glibc-langpack-en && \
		dnf -y install python3-createrepo_c && \
		dnf -y install python3-libmodulemd && \
		dnf -y install python3-libcomps && \
        dnf -y install postgresql && \
        dnf -y install postgresql-server && \
        dnf -y install nginx && \
        dnf -y install redis && \
        dnf -y install python3-setuptools && \
		dnf clean all

RUN     dnf -y install buildah --exclude container-selinux && \
		dnf clean all

# Until the update is re-submitted & released
# https://bodhi.fedoraproject.org/updates/FEDORA-2019-0d122cc67a
RUN rpm -q python3-libcomps --queryformat=%{VERSION}-%{RELEASE} | grep -v 0.1.11-1 || dnf upgrade -y --enablerepo=updates-testing python3-libcomps

RUN sed 's|^#mount_program|mount_program|g' -i /etc/containers/storage.conf

RUN mkdir -p /etc/pulp

RUN easy_install pip

RUN pip3 install pulpcore pulp-file pulp-container pulp-ansible pulp-rpm pulp-maven

RUN echo "/var/lib/pgsql true postgres 0600 0750" >> /etc/fix-attrs.d/postgres
COPY pulpcore-content.run /etc/services.d/pulpcore-content/run

RUN mkdir -p /etc/services.d/nginx /etc/services.d/postgresql /etc/services.d/redis /etc/services.d/pulpcore-worker@1 /etc/services.d/pulpcore-worker@2 /etc/services.d/pulpcore-resource-manager /etc/services.d/pulpcore-api /etc/services.d/pulpcore-content /var/lib/pgsql /var/run/pulpcore-worker-1 /var/run/pulpcore-worker-2 /var/run/pulpcore-resource-manager

COPY postgres.run /etc/services.d/postgresql/run
COPY redis.run /etc/services.d/redis/run
COPY pulpcore-worker@2.run /etc/services.d/pulpcore-worker@2/run
COPY pulpcore-resource-manager.run /etc/services.d/pulpcore-resource-manager/run
COPY pulpcore-api.run /etc/services.d/pulpcore-api/run
COPY postgres.prep /etc/cont-init.d/postgres
COPY pulpcore-worker@1.run /etc/services.d/pulpcore-worker@1/run
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx.run /etc/services.d/nginx/run

RUN mkdir -p /etc/nginx/pulp/

RUN ln /usr/local/lib/python3.7/site-packages/pulp_ansible/app/webserver_snippets/nginx.conf /etc/nginx/pulp/pulp_ansible.conf
RUN ln /usr/local/lib/python3.7/site-packages/pulp_container/app/webserver_snippets/nginx.conf /etc/nginx/pulp/pulp_container.conf

ENTRYPOINT ["/init"]
