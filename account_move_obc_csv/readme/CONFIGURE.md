- Give the accounts the OBC account codes. For an account that stands
  for an OBC sub-account, join the account code and the sub-account code
  with a period: `111.2` is exported as account `111`, sub-account `2`.
- Set *OBC Department Code* in the analytic accounts that stand for a
  department. Only income and expense journal items carry a department;
  the others are exported with the default department code.
- Set *OBC Tax Category* and *OBC Tax Rate Type* in the tax records. Tax
  amounts are exported as separate rows on the tax account, with the tax
  calculation of OBC turned off.
- In the journals (*Advanced Settings \> OBC Export*), tick *Exclude from
  OBC Export* for the journals that must not reach OBC, and set *OBC
  Aggregation* to *Per Month* for the journals to sum into one month-end
  entry, such as the inventory valuation journal.
- In *Accounting \> Configuration \> Settings \> OBC Export*, set the
  department code to export for journal items without a department.
