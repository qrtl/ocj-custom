This module adds a lot/serial number field to journal items.

Unlike the lots that can be derived from the stock moves linked to an invoice
line, this field is stored on the journal item itself. It can therefore be set
on lines that have no delivery behind them (e.g. lines created by an external
system integration, or manually entered invoices), and it can be used to
filter and group journal items by lot/serial number.
