
Licenses for pyEMAPS
====================

GNU General Public License v3.0, with a Linking Exception for emaps
-------------------------------------------------------------------

**pyEMAPS** is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version. This applies to personal and commercial use.

As an additional permission under Section 7 of GNU GPL version 3, the copyright holders of
pyEMAPS permit combining or linking it with *emaps*, its separately licensed simulation engine.
The exception is in the
`license-exception.txt <https://github.com/emlab-solutions/pyemaps/blob/main/license-exception.txt>`_
file, and reads:

    **GPLv3 Linking Exception for Compiled Backend**

    Copyright (C) 2021-2026 EMLab Solutions, Inc.

    The Python frontend package pyEMAPS is licensed under the GNU General Public License,
    version 3 or (at your option) any later version.

    **Additional Permission under GNU GPL version 3, Section 7**

    As a special exception, the copyright holders of pyEMAPS grant permission to combine or link
    this Python frontend with emaps, the simulation engine of EMLab Solutions, Inc. that pyEMAPS
    runs on, including its compiled Fortran, C, and C++ extension modules, notwithstanding that
    the backend modules may be distributed under separate proprietary or commercial licenses.

    You may convey such a combined work, subject to compliance with the GNU GPL applicable to
    pyEMAPS and the applicable license terms governing emaps.

    This exception does not, by itself, require the proprietary backend modules to be licensed
    under the GNU GPL solely because they are combined with the frontend under this permission.

    This exception applies only to code for which the licensors granting this exception have
    the necessary copyright rights. It does not grant additional permissions for third-party
    software or waive obligations under third-party licenses.

    The GNU GPL continues to apply to pyEMAPS, except as expressly permitted by this exception.

    This exception constitutes an additional permission under Section 7 of GNU GPL version 3.

**pyEMAPS** is distributed for electron diffraction and microscopy research, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with **pyEMAPS**, in
its COPYING file. If not, see `<https://www.gnu.org/licenses/>`_.

The emaps Engine and Its Licensed 4D-STEM Features
--------------------------------------------------

*emaps*, the compiled simulation engine that pip installs with pyEMAPS, is not covered by the GNU
General Public License: it's proprietary software of EMLab Solutions, Inc., free only when it's
used with pyEMAPS. Its *license.txt* and *COPYING* files are installed with it.

**NOTE:** The 4D-STEM features of emaps require a separate license for use in commercial or
production environments.

To buy a license for the 4D-STEM features:

1. Write to support@emlabsoftware.com with the license you need.
2. We create your order, and you receive a 19-character license activation token, in the form
   ``XXXX-XXXX-XXXX-XXXX``, by email.
3. Activate the license with the token. Activation works online or offline:

   .. code-block:: console

      pyemaps --license XXXX-XXXX-XXXX-XXXX

4. Check that the license is active:

   .. code-block:: console

      pyemaps --license info

See :ref:`License Activation` for the details, including the 7-day trial license.

Usage of the 4D-STEM features without a valid license may be subject to legal action.

Additional copyright notices and license terms applicable to portions of pyEMAPS are set forth
in the `COPYING <https://github.com/emlab-solutions/pyemaps/blob/main/COPYING>`_ file.

Contact support@emlabsoftware.com for any questions about the license terms.
