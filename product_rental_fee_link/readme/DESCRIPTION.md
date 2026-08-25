This module lets you link rental fee service products to the equipment or
accessory products whose rental they bill. It builds on
``product_classification``, which is what tells equipment and accessories
apart from the other goods.

When rental fees are managed as products separate from the equipment
itself, nothing in the standard data model ties the two together. This
module adds a many2many link between them: **Billed Equipment** on the
rental fee product, and its mirror **Rental Fee Products** on the
equipment or accessory. Either side can add existing records or create new
ones.

Why a dedicated field rather than *Optional Products*: `optional_product_ids`
is a many2many meant for cross-sell suggestions in the quotation product
configurator. It cannot express a restricted, type-checked relationship, and
its meaning collides with genuine cross-sell entries. A dedicated field can
be validated, searched, and used as the source for integrations.
