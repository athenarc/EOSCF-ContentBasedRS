# Licence

<! --- SPDX-License-Identifier: CC-BY-4.0  -- >

## Disaster Recovery

This application is stateless and does not store any information in local storage.

In case of a disaster or major failure the following steps should be taken:

1. Run the `GET` request `/v1/health` and resolve any connection issues with the database.
2. Run the `GET` request `v1/update` to update the internal structures.
3. If the problem persists, restart the container.

More info can be found in [Troubleshooting](troubleshooting.md).
