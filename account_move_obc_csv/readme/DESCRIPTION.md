This module exports the journal entries of a period, once, as a CSV file
to be imported into the OBC accounting system (Kanjo Bugyo i-series, "OBC
receiving format" with the item codes in the first line).

The journal items are not exported one by one. They are summed per
account, sub-account, department and tax into one OBC entry per journal
and day. Cost of sales of invoices, and journals set so, make one entry
dated the last day of the month.

The export depends on the report_csv module from OCA.
