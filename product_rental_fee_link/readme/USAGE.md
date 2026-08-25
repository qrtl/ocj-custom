On an equipment or accessory product, use the **Rental Fee Products** list
in the **Classification** section, directly under **Product Kind**, to
add the service products used to bill its rental. Adding a line there sets
the link on the service product automatically; there is no field to set it
from the service product's own form.

An equipment or accessory may have several rental fee products - for
example a base fee and a separate fee for a specific accessory bundle -
each its own service product rather than a single one carrying every price
as a variant. A rental fee product bills exactly one equipment or
accessory - it cannot be shared between several.

To find equipment that still needs a rental fee product, use the **Rental
Fee Product Missing** filter in the product search view. It lists equipment
and accessories only, so consumables do not drown out the products that
are actually missing a fee product.

If a rental fee product carries variants (for example a *price category*
attribute for first unit / second unit / in-hospital use), the variants of
that product are the set of billable items for the equipment it bills -
which is what an integration reads to publish the corresponding product
codes.
