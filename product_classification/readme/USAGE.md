To classify a product:

1. Open a product; the *Classification* section is on the *General Information*
   tab, below the product category and pricing.
2. Set the **Product Kind** (equipment, accessory, consumable or rental fee),
   the **Manufacturer** and the relevant classification. The equipment
   classification field appears when the kind is equipment, accessory or rental
   fee.

*Rental Fee* is the one kind that is not goods: it is the service billed for
renting equipment, and it carries the classification of the equipment the fee is
charged for, which is what an integration reports on a rental line. Keeping it in
the same field as the goods means one field decides what a product is, rather
than that question being split between the product kind and the product type.

An equipment, accessory or rental fee product cannot be saved without an
equipment classification. The check runs only when the product kind or the classification
itself is written, so products that predate the rule can still be edited for
other fields while their classification is being filled in.

Products can be searched and filtered by manufacturer and classification from
the product list view. The *Classification Missing* and *Product Kind Not Set*
filters list the products whose classification data is still incomplete - the
kind cannot be enforced, since a product without a kind is indistinguishable
from one that legitimately has none.
