Whether a rental is billed pro rata for a partial month is agreed per customer
*and* per piece of equipment: the same customer can be prorated on one device
and billed in full on another. The customer-level switch lives in
`partner_billing_policy`; this module adds the equipment axis to it, as a list
of equipment on the customer. An empty list means every rental the customer
has is prorated, so the common case needs no entry.

Odoo does not compute the prorated amount here. The setting is read by whoever
bills — the rental-fee interface delivers it per customer and product.
