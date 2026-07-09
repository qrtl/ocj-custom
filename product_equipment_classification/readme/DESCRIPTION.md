This module adds two classification axes to products for medical equipment
management:

- **Equipment Classification** (機器分類) — the primary classification of a
  device, used as an important input for downstream logic (for example the
  guided navigation flow).
- **Equipment Sub-Classification** (機器分類サブ) — used to classify auxiliary
  devices.

Each axis is backed by a dedicated, user-maintainable model
(`product.equipment.classification` and
`product.equipment.classification.sub`) holding a name and an optional code
(a numeric code is preferred for integration with external systems). Each
product can be linked to one classification and one sub-classification.

The module ships the models and the configuration UI but no predefined
classifications, so the taxonomy can be tailored to each deployment (for
example through a company-specific data module or an external integration).
