This module adds a **delivery time slot** to transfers, for recording the time of day
the recipient asked the delivery to arrive.

The available slots are held in a dedicated `stock.delivery.time.slot` model with a
**code** and a **name**:

- the **code** is the key exchanged with external systems (for example a system that
  sends delivery orders to Odoo), and should match the carrier's own time slot code
  where the carrier defines one;
- the **name** is the label handed to the warehouse as is, and printed on the waybill.

The module provides the model and the configuration UI but does not ship any slots,
since the set depends on the carrier and on the service contracted with it. Create
them in the UI or load them from a company-specific data module.
