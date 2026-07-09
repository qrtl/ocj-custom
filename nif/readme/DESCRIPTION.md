This module holds the product-side field extensions required by the **Navi in
Flow** (ナビフロー) integration, through which product/equipment master data is
exchanged with the CIAS system.

It is intended as the single place to collect Navi in Flow related fields on
products as the integration grows.

Each product can be flagged as **equipment** or **consumable** (the two flags
are mutually exclusive) and linked to a **Manufacturer** (メーカー).

When a product is flagged as equipment, it can additionally be given the
following two classification axes:

- **Equipment Classification** (機器分類) — the primary classification of a
  device, used as an important input for the Navi in Flow logic.
- **Equipment Sub-Classification** (機器分類サブ) — used to classify auxiliary
  devices.

The manufacturer and each classification axis are backed by dedicated,
user-maintainable models (`product.manufacturer`,
`product.equipment.classification` and
`product.equipment.classification.sub`) holding a name and an optional code
(a numeric code is preferred for integration with external systems). Each
product can be linked to one manufacturer, one classification and one
sub-classification.

The module ships the models and the configuration UI but no predefined
records, so the taxonomy can be tailored to each deployment (for example
through a company-specific data module or the external integration).
