This module adds classification master data to products so that equipment and
consumables can be categorized consistently.

Each product can be flagged as **equipment** or **consumable** (*Product Kind*)
and linked to a **Manufacturer** (メーカー). Depending on the kind, it can then
be given a classification:

- **Equipment Classification** (機器分類) — the primary classification of a
  device, with an **Equipment Sub-Classification** (機器分類サブ) for auxiliary
  devices.
- **Consumable Classification** — the classification of a consumable product.

The manufacturer and each classification axis are backed by dedicated,
user-maintainable models (`product.manufacturer`,
`product.equipment.classification`, `product.equipment.classification.sub` and
`product.consumable.classification`) holding a name and an optional code (a
numeric code is preferred for integration with external systems).

Several of these fields feed the **Navi in Flow** (ナビフロー) integration, which
exchanges product/equipment master data with the CIAS system; the fields
concerned say so in their help text so their purpose stays clear over time.

The module ships the models and the configuration UI but only a small set of
sample equipment classifications, so the taxonomy can be tailored to each
deployment (for example through a company-specific data module or the external
integration).
