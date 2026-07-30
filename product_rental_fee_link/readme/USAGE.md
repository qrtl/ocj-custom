On an equipment product (Goods), set **Rental Fee Product** next to the product
category. Only non-storable service products can be selected, and a product
cannot point at itself.

The field is hidden on service products, since a rental fee product is not
itself rented.

To find equipment that still needs the link, use the **Rental Fee Product
Missing** filter in the product search view.

Several equipment products may share the same rental fee product; this is not
restricted, because the same fee often applies to more than one model.

If the rental fee product carries variants (for example a *price category*
attribute for first unit / second unit / in-hospital use), the variants of the
linked product are the set of billable items for that equipment - which is what
an integration reads to publish the corresponding product codes.
