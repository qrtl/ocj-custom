This module adds a **Product Kind** to putaway rules (the kind set on the product
by `product_classification`: Equipment, Accessory, Consumable or Rental Fee). A
rule with a product kind applies only to products of that kind; a rule without
one applies as in standard Odoo.

A rule with a product kind and no product or category is ranked like a standard
rule with neither: among such rules, the priority (sequence) decides, and a rule
whose priority was never set comes after those with one.
