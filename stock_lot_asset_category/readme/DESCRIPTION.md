This module records who owns each serial/lot number in an **asset category**
(for example own asset, or an asset of the company it is rented from).

A dedicated `stock.lot.asset.category` model holds the categories, so they can
be maintained by users instead of being hard-coded. The module does not ship
any category (they can be provided by a company-specific data module).

Each product carries a **default asset category**. A new serial/lot number
takes it from its product, and it can then be changed on that serial/lot
number alone, for units that are an exception to their product's default.
Changing the default of a product does not change its existing serial/lot
numbers.

Because the asset category says who owns a unit, only the users of the group
*Assign Asset Categories to Products and Lots/Serials* can set it, on a product
or on a serial/lot number. For everybody else the default of the product is
hidden, and the asset category of a serial/lot number is read-only, in the
forms and through imports alike.
