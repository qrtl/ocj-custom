This module records the **payer** of a customer: the contact that settles its
invoices, when the money comes from another entity.

A group of contacts billed one by one but paid for centrally by its head
office is the case it is meant for. The invoices stay issued to, and accounted
for, the customer; only the payment arrives from the payer. Reconciliation
reads this field to know which open items a payment from the payer may settle,
and the payer is what a bank transaction from the group is attributed to.

The relation is one level deep: a payer cannot itself be paid for by someone
else, and a contact others already point at cannot start being paid for. Point
every member of a group at the same payer instead.
