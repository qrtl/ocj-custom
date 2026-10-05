On a rental fee product - any service - the **Rental Set** tab holds **Set
Components**: the equipment and accessories that this one product bills
together. "Add a line" searches the existing equipment and accessories;
consumables are billed on their own and are not offered.

Register a fee for a single machine as a set of one. That is what makes the
product findable both ways: from the machine, and from a lookup that asks
about that machine alone.

Components are products, not variants, so an import can name them by the
product's external ID (``rental_set_component_ids/id``) or internal reference.
The same combination may be entered on several rental fee products.

On an equipment or accessory, the same tab shows **Rental Fee Sets**
read-only: the rental fee products whose set contains it. A set is
maintained from the fee product, which is where it is one list rather than
one row per member.

In the product search view, the **Rental Set** filter lists the rental fee
products that have a set, **Rental Fee Product Missing** lists the equipment
and accessories no set contains yet, and **Set Components** searches the sets
a given machine appears in.
