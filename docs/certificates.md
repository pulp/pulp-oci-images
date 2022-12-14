# CERTIFICATES

By default, running the Multi-Process image with https image tag (`pulp/pulp:https`) will create and configure a self-signed certificate in Nginx.  
This documentation provide the steps to configure a custom certificate instead of using the provided self-signed.

There are a lot of excelent tools to generate X.509 certificates, like [`OpenSSL`](https://github.com/openssl/openssl), [`Vault`](https://developer.hashicorp.com/vault/tutorials/secrets-management/pki-engine), [Let's Encrypt](https://letsencrypt.org/getting-started/), etc.  
It is out of scope of this document to provide the steps to install or configure them.  

> :information_source: The following steps are meant to be a starting point to create a **test** certificate and configure it in Pulp multi-process containers.


## GENERATING A NEW CERTIFICATE

> :information_source: The following steps are optional in case a certificate is already available.

The current image of Pulp multi-process container comes with `openssl` installed.  
It also comes with an [init script](https://github.com/pulp/pulp-oci-images/blob/latest/images/s6_assets/init/certs) that generates a default certificate in case none is provided.

Here is an example of how to create a new custom certificate using `openssl`:
* create a self-signed certificate with `Subject: CN=$MY_DOMAIN` and the additional hosts (SubjectAlternativeName) `$CERT_SAN`
```console
$ podman exec -it pulp bash
[root@f14649b06e01 /]# MY_DOMAIN=pulp.example.com
[root@f14649b06e01 /]# CERTS_DIR=/etc/pulp/certs
[root@f14649b06e01 /]# CERT_SAN="subjectAltName=IP:0.0.0.0,DNS:pulp,DNS:pulp.example.com,DNS:localhost"
[root@f14649b06e01 /]# openssl req -x509 -nodes -newkey rsa:2048 -keyout ${CERTS_DIR}/pulp_webserver.key -out ${CERTS_DIR}/pulp_webserver.crt -days 365  -subj "/CN=$MY_DOMAIN" -addext $CERT_SAN
[root@f14649b06e01 /]# chgrp pulp ${CERTS_DIR}/pulp_webserver.crt ${CERTS_DIR}/pulp_webserver.key
```

* check the certificate content
```console
[root@c20257cd4dd4 /]# openssl x509 -noout -text -in ${CERTS_DIR}/pulp_webserver.crt
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            7a:ff:8d:e3:92:02:bf:6e:ad:76:ea:45:1c:80:ea:fd:49:c2:da:5e
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: CN = pulp.example.com
        Validity
            Not Before: Dec 13 13:17:29 2022 GMT
            Not After : Dec 13 13:17:29 2023 GMT
        Subject: CN = pulp.example.com
        Subject Public Key Info:
...
```


## CONFIGURING A CUSTOM SERVER CERTIFICATE IN NGINX

### **Configuring the new custom certificate**

To use the custom certificate created using the steps from [*GENERATING A NEW CERTIFICATE*](#generating-a-new-certificate):
* copy the certificates into `/etc/pki/tls/certs/` directory:
> :warning: make sure to not modify the destination file names and path (`/etc/pki/tls/certs/pulp_webserver.crt` and `/etc/pki/tls/private/pulp_webserver.key`) because these are the names configured in Nginx
```console
$ podman exec -it pulp bash
[root@f14649b06e01 /]# cp /etc/pulp/certs/pulp_webserver.crt /etc/pki/tls/certs/pulp_webserver.crt
cp: overwrite '/etc/pki/tls/certs/pulp_webserver.crt'? y
[root@f14649b06e01 /]# cp /etc/pulp/certs/pulp_webserver.key /etc/pki/tls/private/pulp_webserver.key
cp: overwrite '/etc/pki/tls/private/pulp_webserver.key'? y
```

* restart nginx process to get the new certificate
```
$ podman exec pulp s6-svc -r /run/service/nginx
```

* verify that Nginx is now using the new certificate
```
$ podman exec pulp  openssl s_client -connect pulp:443
Can't use SSL_get_servername
depth=0 CN = pulp.example.com
verify error:num=18:self signed certificate
verify return:1
depth=0 CN = pulp.example.com
verify return:1
CONNECTED(00000003)
---
Certificate chain
 0 s:CN = pulp.example.com
   i:CN = pulp.example.com
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDTTCCAjWgAwIBAgIUZFS+5+hhWrM270+X+k8vpfwIQL8wDQYJKoZIhvcNAQEL
BQAwGzEZMBcGA1UEAwwQcHVscC5leGFtcGxlLmNvbTAeFw0yMjEyMTQxNzMxMzda
Fw0yMzEyMTQxNzMxMzdaMBsxGTAXBgNVBAMMEHB1bHAuZXhhbXBsZS5jb20wggEi
...
-----END CERTIFICATE-----
subject=CN = pulp.example.com
issuer=CN = pulp.example.com
```

### **Configuring an existing certificate**

It is also possible to bring your own company certificate instead of creating a new one through [*GENERATING A NEW CERTIFICATE*](#generating-a-new-certificate) steps.

* copy the certificates into `/etc/pulp/certs/` directory. This will prevent having to copy the certificates again in case of a container reprovisioning (the certificates will be persisted in container volume):
```console
$ podman cp my-company-generated-certificate.crt pulp:/etc/pulp/certs/pulp_webserver.crt
$ podman cp my-company-generated-certificate.key pulp:/etc/pulp/certs/pulp_webserver.key
```

* now, copy the certificates into `/etc/pki/tls/certs/` directory:
> :warning: make sure to not modify the destination file names and path (`/etc/pki/tls/certs/pulp_webserver.crt` and `/etc/pki/tls/private/pulp_webserver.key`) because these are the names configured in Nginx
```console
$ podman exec -it pulp bash
[root@f14649b06e01 /]# cp /etc/pulp/certs/pulp_webserver.crt /etc/pki/tls/certs/pulp_webserver.crt
cp: overwrite '/etc/pki/tls/certs/pulp_webserver.crt'? y
[root@f14649b06e01 /]# cp /etc/pulp/certs/pulp_webserver.key /etc/pki/tls/private/pulp_webserver.key
cp: overwrite '/etc/pki/tls/private/pulp_webserver.key'? y
```

* restart nginx process to get the new certificate
```
$ podman exec pulp s6-svc -r /run/service/nginx
```


* verify that Nginx is now using the new certificate
```
$ podman exec pulp  openssl s_client -connect pulp:443
Can't use SSL_get_servername
depth=0 CN = /test
depth=0 CN = /test
CONNECTED(00000003)
---
Certificate chain
 0 s:CN = my-company-domain
   i:CN = my-company-domain
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDTTCCAjWgAwIBAgIUZFS+5+hhWrM270+X+k8vpfwIQL8wDQYJKoZIhvcNAQEL
BQAwGzEZMBcGA1UEAwwQcHVscC5leGFtcGxlLmNvbTAeFw0yMjEyMTQxNzMxMzda
Fw0yMzEyMTQxNzMxMzdaMBsxGTAXBgNVBAMMEHB1bHAuZXhhbXBsZS5jb20wggEi
...
-----END CERTIFICATE-----
subject=CN = my-company-domain
issuer=CN = my-company-domain
```

## SETTING UP ADDITIONAL TRUSTED CAs

Use the following steps to set up additional certificate authorities (CA) to be trusted by the services running in Pulp container.

```console
$ podman cp my-company-CA.crt pulp:/etc/pki/ca-trust/source/anchors/
$ podman exec pulp update-ca-trust
```

* check the ca-trust list
```console
$ podman exec pulp grep pulp.example.com -A20 /etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt
# pulp.example.com
-----BEGIN TRUSTED CERTIFICATE-----
MIIDFzCCAf+gAwIBAgIUBd+SIbUJPVSgO2jR9mgtoGfRo3IwDQYJKoZIhvcNAQEL
BQAwGzEZMBcGA1UEAwwQcHVscC5leGFtcGxlLmNvbTAeFw0yMjEyMTMxMzI1MDFa
...
-----END TRUSTED CERTIFICATE-----
```

To avoid having to run these steps everytime a new container is provisioned, it is also possible to create a new image with the CA built in it:
```console
$ cat<<EOF | podman build -t my_pulp_image -f- .
FROM quay.io/pulp/pulp:latest
COPY my-company-CA.crt /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust
EOF
```
