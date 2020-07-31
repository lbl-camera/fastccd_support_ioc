=====
Usage
=====

To launch this IOC, there is an entrypoint installed at setup.

.. code-block:: console

    $ fastccd_support_ioc --list-pvs

At COSMIC-Scattering, this IOC is already deployed as a service, and must be stopped before starting a new instance to
avoid cross-talk.

.. code-block:: console

    $ systemctl stop fastccd_support_ioc.service
