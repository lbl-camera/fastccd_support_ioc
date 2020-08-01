# Usage


To launch this IOC, there is an entrypoint installed at setup.

```bash
fastccd_support_ioc --list-pvs
```

At COSMIC-Scattering, this IOC is already deployed as a service, and must be stopped before starting a new instance to
avoid cross-talk.

```bash
systemctl stop fastccd_support_ioc.service
```

The following PVs are included under the PV group named "fccd_support_ioc":

- `fccd_support_ioc:state`
- `fccd_support_ioc:initialize`
- `fccd_support_ioc:shutdown`
