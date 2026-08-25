On a rental fee service product, set **Billed Equipment** in the
**Classification** section, directly under **Product Kind**. Only equipment
and accessory products can be selected, and a product cannot point at itself.

The field is shown only when the product kind is rental fee. On an equipment
or accessory product, the reverse **Rental Fee Products** list shows every
service product billing its rental.

To find equipment that still needs a rental fee product, use the **Rental
Fee Product Missing** filter in the product search view. It lists equipment
and accessories only, so consumables do not drown out the products that are
actually missing a fee product.

An equipment or accessory may have several rental fee products - for example
a base fee and a separate fee for a specific accessory bundle - each its own
service product rather than a single one carrying every price as a variant.

If a rental fee product carries variants (for example a *price category*
attribute for first unit / second unit / in-hospital use), the variants of
that product are the set of billable items for the equipment it bills -
which is what an integration reads to publish the corresponding product
codes.
