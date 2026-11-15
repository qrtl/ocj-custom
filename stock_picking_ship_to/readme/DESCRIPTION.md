This module adds a **ship-to name, address and phone** to transfers, as plain text,
for destinations that are not partners in Odoo (for example a patient's home given by
an external system with each order) and for systems that take the destination as text.

The fields default from the transfer's partner and stay editable:

- **name**: the partner's name, or for a contact, its company and its name joined by a
  full-width space;
- **address**: state, city, street and street 2 on one line, in Japanese order;
- **phone**: the partner's phone.

A value given when the transfer is created, or written later, is kept until the
partner changes.
