This module lets you point a rental fee service product at the equipment or
accessory product whose rental it bills. It builds on ``product_classification``,
which is what tells equipment and accessories apart from the other goods.

When rental fees are managed as products separate from the equipment itself,
nothing in the standard data model ties the two together. This module adds a
dedicated **Billed Equipment** link on the rental fee product, restricted to
equipment and accessory products, together with the reverse **Rental Fee
Products** list on the equipment or accessory itself.

Why a dedicated field rather than *Optional Products*: `optional_product_ids` is
a many2many meant for cross-sell suggestions in the quotation product
configurator. It cannot express a single, verifiable relationship, it carries no
type restriction, and its meaning collides with genuine cross-sell entries. A
dedicated many2one can be validated, searched, and used as the source for
integrations.
