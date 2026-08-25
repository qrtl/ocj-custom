On an equipment or accessory product, use the **Rental Fee Products** list
in the **Classification** section, directly under **Product Kind**, to
link the service products used to bill its rental. Because the link is a
many2many, "Add a line" can search for an already existing rental fee
product or create a new one - there is no separate field to set on the
rental fee product's own form.

An equipment or accessory may have several rental fee products - for
example a base fee and a separate fee for a specific accessory bundle -
each its own service product rather than a single one carrying every
price as a variant. A rental fee product may in turn bill several
equipment or accessory products, when the same fee genuinely applies to
more than one.

To find equipment that still needs a rental fee product, use the **Rental
Fee Product Missing** filter in the product search view. It lists equipment
and accessories only, so consumables do not drown out the products that
are actually missing a fee product. The same search view also lets you
filter by **Billed Equipment** to look up a rental fee product's
equipment from the other direction.

If a rental fee product carries variants (for example a *price category*
attribute for first unit / second unit / in-hospital use), the variants of
that product are the set of billable items for the equipment it bills -
which is what an integration reads to publish the corresponding product
codes.
