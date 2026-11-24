This module limits the products a stock location accepts by their product kind
(set on the product by `product_classification`). A location can be set to
accept:

- **Equipment and Accessories Only**: products of kind Equipment or Accessory,
  whether or not they are tracked by serial number;
- **Consumables Only**: products of kind Consumable.

Products with no product kind, such as gas cylinders, are not checked and can be
put in any location. Products of any other kind are refused.

Validating a transfer or applying an inventory adjustment that would put any
other product in the location is refused, with the product and the location
named in the error. Editing the destination or the quantity of a done move line
is checked the same way.

The setting applies to the location and to its sublocations; a sublocation
with its own setting follows that setting instead. It only checks stock coming
in: stock already in the location when the setting is made is left as it is,
and can still be moved out.
