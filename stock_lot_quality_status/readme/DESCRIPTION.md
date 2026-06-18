This module adds a configurable **quality status** to serial/lot numbers.

A dedicated `stock.lot.quality.status` model holds the available statuses, so
they can be maintained by users instead of being hard-coded. Each lot/serial
number can then be assigned one of these statuses.

The module provides the model and the configuration UI but does not ship any
predefined statuses, so the classification can be tailored to each deployment
(for example through a company-specific data module).

Each status carries:

- a **major category** used as the aggregation axis for inventory and
  accounting reports;
- a **shippability** flag (shippable / conditional / not shippable) shown with a
  colour in the list;
- an optional **shippability note** for qualifiers such as *ship A-grade first*
  or *repair vendor only*;
- a **shipping priority** for ordering shippable stock; and
- a **default** flag so newly created lots/serials receive a status
  automatically.

The status is informational on its own. It is intended as a foundation for
features that act on it — for example restricting whether stock with a given
quality status can be shipped, or automating status transitions on receipt and
repair returns — which can be layered on top in separate modules.
