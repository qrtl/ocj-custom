On an equipment product, set **Rental Fee Product** in the **Classification**
section, directly under **Product Kind**. Only service products can be
selected, and a product cannot point at itself.

The field is shown only when the product kind is equipment or accessory. That
is the only distinction available: equipment, accessories and consumables are
all goods, so the product type cannot tell them apart, and a rental fee product
is not itself rented.

To find equipment that still needs the link, use the **Rental Fee Product
Missing** filter in the product search view. It lists equipment and accessories
only, so consumables do not drown out the products that are actually missing a
fee product.

Several equipment products may share the same rental fee product; this is not
restricted, because the same fee often applies to more than one model.

If the rental fee product carries variants (for example a *price category*
attribute for first unit / second unit / in-hospital use), the variants of the
linked product are the set of billable items for that equipment - which is what
an integration reads to publish the corresponding product codes.
