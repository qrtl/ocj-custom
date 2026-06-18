This module tracks the installation status of serial/lot numbers (`stock.lot`), and
surfaces that status on location-level stock (`stock.quant`).

It adds the following information to each serial/lot number:

- Installation status (Not Installed / Installed)
- Installation status change date
- Installation completion date

The status change date and completion date are maintained automatically when the
installation status changes, and changes are logged in the lot's chatter. The same
information is mirrored (read-only) on inventory quants so it can be reviewed per
location.
