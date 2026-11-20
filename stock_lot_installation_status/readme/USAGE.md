To set the installation status of a serial/lot number:

1. Go to *Inventory > Products > Lots/Serial Numbers*.
2. Open a lot/serial number.
3. In the *Installation Information* section, set the *Installation Status*.

When the status changes:

- The *Installation Status Change Date* is set to the current date.
- When the status changes to *Installed*, the *Installation Completion
  Date* is set to the current date.
- When the status changes back to *Not Installed*, the *Installation
  Completion Date* is kept (it is not cleared).
- The *First Installation Date* is set the first time the status becomes
  *Installed* and is never refreshed afterwards, so a lot that is recovered and
  installed again keeps its original date. The *Installation Completion Date*
  follows the latest installation instead.

The *First Installation Date* is read-only for everyone except a system
administrator, who can correct it — the automatic value is only as good as the
first status change recorded in Odoo, so equipment installed before this module
was in use has to be filled in by hand. Changes to all four values are logged in
the lot's chatter.

The installation status and the three dates are also shown (read-only) on
inventory quants under *Inventory > Reporting > Locations*, and can be used to
filter and group records. The *First Installation Date* column is hidden by
default.
