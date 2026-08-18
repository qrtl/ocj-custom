Two settings are needed for a transaction to be reconciled without any manual
step.

1. Set the system parameter `account_accountant.bank_rec_payment_tolerance` to
   the relative difference between an invoice and its payment that should still
   count as a match, e.g. `0.03` for 3%. It is `0` out of the box, which
   disables the matching this module builds on.
2. On the fee model of the bank journal, named *Fees (journal)* and created the
   first time an accountant puts a leftover amount on an account, set the
   account and taxes of the write-off and switch its trigger to *Automated*.

A transaction is then reconciled on import when its partner is identified, a
single open invoice of that partner is within the tolerance, and the leftover
amount is below 3% of the amount received. That 3% is Odoo's own limit and is
not configurable.

Anything else is left untouched for the accountant, in particular a transaction
that matches no invoice and one whose fee exceeds 3% of the amount received.
