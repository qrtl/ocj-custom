This module lets the bank fee reconciliation model of a journal post its entry
by itself, so that a transfer whose bank charge was deducted by the payer is
reconciled without any manual step.

Odoo already recognises this situation: when a transaction is close enough to
an open invoice, it reconciles the invoice in full and leaves the difference on
the suspense account, ready for the journal's fee model. Applying that model is
still a click per transaction, which does not scale to the volume of incoming
transfers a Japanese company receives, as banks there let the payer deduct the
transfer charge.

Setting the fee model to run automatically is not enough on its own: a model
with no matching condition of its own is offered for every unmatched
transaction, and would write off the full amount received to the fee account.
This module keeps the fee model confined to the route that checks the leftover
against the amount received, so it only ever posts what is actually a fee.
