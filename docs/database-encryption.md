# DATABASE ENCRYPTION

Pulp uses a symmetric fernet key to encrypt sensitive fields in the database.  
The default location of the key is `/etc/pulp/certs/database_fields.symmetric.key`.

The key is automatically generated and is stored in `/etc/pulp/certs/database_fields.symmetric.key`.  
The script to generate the key can be found at: https://github.com/pulp/pulp-oci-images/blob/latest/images/s6_assets/init/db-fields-key-create

* list of commands that [`db-fields-key-create`](https://github.com/pulp/pulp-oci-images/blob/latest/images/s6_assets/init/db-fields-key-create) script runs to generate the key:
```bash
openssl rand -base64 32 > /etc/pulp/certs/database_fields.symmetric.key
chmod 640 /etc/pulp/certs/database_fields.symmetric.key
chown root:pulp /etc/pulp/certs/database_fields.symmetric.key
```

## ROTATING THE DATABASE ENCRYPTION KEY

It is **not** possible to rotate the database encryption key yet.  
Check `pulpcore` [issue #2048](https://github.com/pulp/pulpcore/issues/2048) for further information: https://github.com/pulp/pulpcore/issues/2048