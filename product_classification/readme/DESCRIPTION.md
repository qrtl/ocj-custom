This module adds classification master data to products so equipment and
consumables can be categorized consistently.

Each product can be flagged as **equipment**, **accessory**, **consumable** or
**rental fee** (*Product Kind*) and linked to a **Manufacturer** (メーカー), then
given a classification:

- **Equipment Classification** (機器分類) for equipment and accessories, and for
  the rental fee charged against equipment of that classification.

Products can also be given a **Middle Category** (中分類) and a **Minor
Category** (小分類).

Each axis is backed by a dedicated, user-maintainable model holding a name and
an optional code (a numeric code is preferred for integration with external
systems). Several fields feed the **Navi in Flow** (ナビフロー) integration,
which exchanges product/equipment master data with the CIAS system.
