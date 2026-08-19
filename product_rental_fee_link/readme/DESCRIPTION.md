This module lets you point an equipment product at the service product used to
bill its rental. It builds on ``product_classification``, which is what tells
equipment and accessories apart from the other goods.

When rental fees are managed as products separate from the equipment itself
(one *rental fee* product per equipment model), nothing in the standard data
model ties the two together. This module adds a dedicated **Rental Fee Product**
link on the product, restricted to service products.

Why a dedicated field rather than *Optional Products*: `optional_product_ids` is
a many2many meant for cross-sell suggestions in the quotation product
configurator. It cannot express a single, verifiable relationship, it carries no
type restriction, and its meaning collides with genuine cross-sell entries. A
dedicated many2one can be validated, searched, and used as the source for
integrations.
