This module limits the products a stock location accepts by whether they are
tracked by serial or lot number. A location can be set to accept:

- **Serial- or Lot-Tracked Only**: products tracked by serial or lot number;
- **Quantity-Tracked Only**: products tracked by quantity only, with neither
  serial nor lot numbers.

Validating a transfer or applying an inventory adjustment that would put any
other product in the location is refused, with the products and the location
named in the error. Editing the destination of a done move line to such a
location is refused the same way.

The setting applies to the location and to its sublocations; a sublocation
with its own setting follows that setting instead. It only checks stock coming
in: stock already in the location when the setting is made is left as it is,
and can still be moved out.
