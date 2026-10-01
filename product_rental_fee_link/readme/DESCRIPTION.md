This module lets you record the products a rental fee service product bills,
as the exact set it bills them in. It builds on ``product_classification``,
which is what tells equipment and accessories apart from the other goods.

Rental fees are managed as service products, separate from the equipment
itself, and nothing in the standard data model ties the two together. A fee
is often charged for a combination rather than a single machine - a
concentrator together with a demand valve and a flow meter, say - and the
combination is what decides which product prices it.

**Set Components** on the rental fee product holds that combination, and
**Rental Fee Sets** on the equipment or accessory shows it from the other
side: which fees bill this product. A fee for a single machine is a set of
one, so both directions are answered by the same relation.

``_find_by_rental_set()`` returns the rental fee products whose set is
*exactly* the combination asked for, which is what turns a selection of
equipment into the product that bills it. The match is exact on purpose:
whether a partly installed set is billed as the set or as its members
individually is a billing decision, and nothing on the product records it -
so the caller asks about each combination it wants priced.

Two details worth knowing:

- **Components are variants** (``product.product``), not templates. That is
  the record a serial, a stock line and the equipment-model interface all
  carry, so a combination coming from outside can be compared with what is
  stored, with no template hop in between.
- **Consumables are not part of a set.** They are billed on their own.

Why a dedicated field rather than *Optional Products*: ``optional_product_ids``
is a many2many meant for cross-sell suggestions in the quotation product
configurator. It cannot express a restricted, type-checked relationship, and
its meaning collides with genuine cross-sell entries. A dedicated field can be
validated, searched, and used as the source for integrations.
