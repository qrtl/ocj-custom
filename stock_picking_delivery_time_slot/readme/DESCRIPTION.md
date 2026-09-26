This module adds a **delivery time slot** to transfers, for recording the time of day
the recipient asked the delivery to arrive.

The available slots are held in a dedicated `stock.delivery.time.slot` model with a
**code** and a **name**:

- the **code** is the key exchanged with external systems (for example a system that
  sends delivery orders to Odoo), and matches the carrier's own time slot code where
  the carrier defines one;
- the **name** is the label handed to the warehouse as is, and printed on the waybill.

The module ships the time slots of Sagawa Express (佐川急便), with Sagawa's codes, plus
a "no preference" slot:

| Code | Name |
|---|---|
| 00 | 指定なし |
| 01 | 午前中 |
| 12 | 12:00～14:00 |
| 14 | 14:00～16:00 |
| 16 | 16:00～18:00 |
| 18 | 18:00～20:00 |
| 04 | 18:00～21:00 |
| 19 | 19:00～21:00 |

Code 00 is not a Sagawa code. Sagawa leaves the field empty when there is no
preference, but a warehouse file that requires the field needs a value to send.

Sagawa offers the evening slots in two sets that cannot be combined: codes 18 and 19
belong to the six-slot service, and code 04 to the five-slot service. Archive the
slots of the set your carrier contract does not use.
