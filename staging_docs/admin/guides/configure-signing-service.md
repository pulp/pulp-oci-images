
# Configure a Signing Service

!!! warning

     Content Signing is in tech-preview and may change in backwards incompatible ways in future releases.

It is possible to sign Pulp's metadata so that users can verify the authenticity of an object.  
This is done by enabling the *Signing Services* feature. The steps to enable it are:

* [create a gpg key](#creating-a-gpg-key)
* [create the signing script](#creating-the-collection-signing-script)
* [create the signing services](#creating-the-signing-services)


For further information, see:

* [pulpcore documentation](site:pulpcore/docs/admin/guides/sign-metadata/) for details on ***Content Signing***
* [pulp_container documentation](site:pulp_container/docs/admin/guides/sign-image/) for details on ***Container Image Signing***


## Creating a gpg key

* open a shell in `pulp` container
> :information_source: Make sure to run the `exec` with `-u pulp`.
```console
$ podman exec -u pulp -it pulp bash
```

* generate a gpg key for user `pulp@example.com`
```console
bash-4.4$ GPG_EMAIL=pulp@example.com
bash-4.4$ cat >/tmp/gpg.txt <<EOF
%echo Generating a basic OpenPGP key
Key-Type: default
Key-Length: 4096
Subkey-Type: default
Subkey-Length: default
Name-Real: Collection Signing Service
Name-Comment: with no passphrase
Name-Email: $GPG_EMAIL
Expire-Date: 0
%no-ask-passphrase
%no-protection
# Do a commit here, so that we can later print "done" :-)
%commit
%echo done
EOF

bash-4.4$ mkdir -m 700 /var/lib/pulp/.gnupg/
bash-4.4$ gpg --batch --gen-key /tmp/gpg.txt
```

* verify the list of available keyrings
```console
bash-4.4$ gpg --list-keys
/var/lib/pulp/.gnupg/pubring.kbx
--------------------------------
pub   rsa4096 2022-12-14 [SC]
      66BBFE010CF70CC92826D9AB71684D7912B09BC1
uid           [ultimate] Collection Signing Service (with no passphrase) <pulp@example.com>
sub   rsa2048 2022-12-14 [E]
```

The above uid will be used in [*create the signing services*](#creating-the-signing-services) step.  
See the GnuPG official documentation for more information on how to generate a new keypair: https://www.gnupg.org/gph/en/manual/c14.html

## Creating the collection signing script

Administrators can add *Signing Services* to Pulp using the command line tools. Users may then associate the *Signing Services* with repositories that support content signing.  
To do so, the first thing needed is to create a script that will be used by the *Signing Service*.

* open a shell in `pulp` container
```console
$ podman exec -it -u pulp pulp bash
```

* example of a *collection signing script*
```console
bash-4.4$ SIGNING_SCRIPT_PATH=/var/lib/pulp/scripts
bash-4.4$ COLLECTION_SIGNING_SCRIPT=my_collection_signing_script.sh
bash-4.4$ cat<<EOF> "$SIGNING_SCRIPT_PATH/$COLLECTION_SIGNING_SCRIPT"
#!/usr/bin/env bash
set -u
FILE_PATH=\$1
SIGNATURE_PATH="\$1.asc"

ADMIN_ID="\$PULP_SIGNING_KEY_FINGERPRINT"
PASSWORD="password"

# Create a detached signature
gpg --quiet --batch --pinentry-mode loopback --yes --passphrase \
   \$PASSWORD --homedir ~/.gnupg/ --detach-sign --default-key \$ADMIN_ID \
   --armor --output \$SIGNATURE_PATH \$FILE_PATH

# Check the exit status
STATUS=\$?
if [ \$STATUS -eq 0 ]; then
   echo {\"file\": \"\$FILE_PATH\", \"signature\": \"\$SIGNATURE_PATH\"}
else
   exit \$STATUS
fi
EOF

bash-4.4$ chmod +x "$SIGNING_SCRIPT_PATH/$COLLECTION_SIGNING_SCRIPT"
```

The script should print out a JSON structure with the following format. All the file names are relative paths inside the current working directory:
```json
{"file": "filename", "signature": "filename.asc"}
```


## Creating the container signing script

Administrators can add a container manifest *Signing Services* to the Pulp Registry using the command line tools. Users may then associate the *Signing Services* with container repositories.  
To do so, the first thing needed is to create a script that will be used by the *Signing Service*.

* open a shell in `pulp` container
```console
$ podman exec -it -u pulp pulp bash
```

* example of a *container signing script*
```console
bash-4.4$ SIGNING_SCRIPT_PATH=/var/lib/pulp/scripts
bash-4.4$ CONTAINER_SIGNING_SCRIPT=my_container_signing_script.sh
bash-4.4$ cat<<EOF> "$SIGNING_SCRIPT_PATH/$CONTAINER_SIGNING_SCRIPT"
#!/usr/bin/env bash
set -u

MANIFEST_PATH=\$1
IMAGE_REFERENCE="\$REFERENCE"
SIGNATURE_PATH="\$SIG_PATH"

skopeo standalone-sign \
      \$MANIFEST_PATH \
      \$IMAGE_REFERENCE \
      \$PULP_SIGNING_KEY_FINGERPRINT \
      --output \$SIGNATURE_PATH

# Check the exit status
STATUS=\$?
if [ \$STATUS -eq 0 ]; then
  echo {\"signature_path\": \"\$SIGNATURE_PATH\"}
else
  exit \$STATUS
fi
EOF

bash-4.4$ chmod +x "$SIGNING_SCRIPT_PATH/$CONTAINER_SIGNING_SCRIPT"
```

The script should print out a JSON structure with the following format. The path of the created signature is a relative path inside the current working directory:
```json
{"signature_path": "signature"}
```

## Creating the signing services


* open a shell in `pulp` container
```console
$ podman exec -it -u pulp pulp bash
```

* get the subkey fingerprint from `pulp@example.com` (the same uid from [*creating a gpg key*](#creating-a-gpg-key))
```console
bash-4.4$ KEY_UID=pulp@example.com
bash-4.4$ export PULP_SIGNING_KEY_FINGERPRINT=$(gpg --with-colons --list-keys ${KEY_UID}|awk -F: '/sub/{getline;print $10;exit}')
```

* create the collection signing service
```console
bash-4.4$ COLLECTION_SIGNING_SERVICE="ansible-default"
bash-4.4$ COLLECTION_SIGNING_SCRIPT=/var/lib/pulp/scripts/my_collection_signing_script.sh
bash-4.4$ /usr/local/bin/pulpcore-manager add-signing-service ${COLLECTION_SIGNING_SERVICE} ${COLLECTION_SIGNING_SCRIPT} ${PULP_SIGNING_KEY_FINGERPRINT}
```

* create the container signing service
```console
bash-4.4$ CONTAINER_SIGNING_SERVICE="container-default"
bash-4.4$ CONTAINER_SIGNING_SCRIPT=/var/lib/pulp/scripts/my_container_signing_script.sh
bash-4.4$ /usr/local/bin/pulpcore-manager add-signing-service ${CONTAINER_SIGNING_SERVICE} ${CONTAINER_SIGNING_SCRIPT} ${PULP_SIGNING_KEY_FINGERPRINT}  --class container:ManifestSigningService
```


## Verifying the signing services

* To check the signing services, make a request to `/pulp/api/v3/signing-services/` endpoint. For example:
```console
$ podman exec pulp curl -Ls -u admin:password localhost:24817/pulp/api/v3/signing-services/ |jq
```
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "pulp_href": "/pulp/api/v3/signing-services/95f7fb89-d134-42e3-8fb1-3565dfbe2583/",
      "pulp_created": "2022-12-12T16:01:34.912449Z",
      "name": "ansible-default",
      "public_key": "-----BEGIN PGP PUBLIC KEY BLOCK-----\n\nmQINBGOTMxwBEADNF...MJfhcG0MpAsiQ\n=/r5T\n-----END PGP PUBLIC KEY BLOCK-----\n",
      "pubkey_fingerprint": "0141A0760878E84C4854BEC43EBAAB0BBB58CFDB",
      "script": "/var/lib/pulp/scripts/my_collection_signing_script.sh"
    },
    {
      "pulp_href": "/pulp/api/v3/signing-services/0b5bbb01-8768-4fa9-b4bc-441f24ced42a/",
      "pulp_created": "2022-12-12T16:29:55.007360Z",
      "name": "container-default",
      "public_key": "-----BEGIN PGP PUBLIC KEY BLOCK-----\n\nmQINBGOTMxwBEADNFkuhOVkQR...MJfhcG0MpAsiQ\n=/r5T\n-----END PGP PUBLIC KEY BLOCK-----\n",
      "pubkey_fingerprint": "0141A0760878E84C4854BEC43EBAAB0BBB58CFDB",
      "script": "/var/lib/pulp/scripts/my_container_signing_script.sh"
    }
  ]
}
```
