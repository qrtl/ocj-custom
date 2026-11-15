Open a delivery order: the **Ship-to Name**, **Ship-to Address** and **Ship-to Phone**
fields are on the **Integration** tab. They are filled from the partner when it is set;
change them when the goods go somewhere else.

Modules that connect transfers to other systems can add their own group to the same
tab (`page[@name='integration']`). The tab shows on deliveries only. To show it on
other transfers, or to hide the ship-to group (`group[@name='ship_to']`) where the
destination means nothing, extend the condition rather than replace it, so that the
conditions of several modules combine:

```xml
<page name="integration" position="attributes">
    <attribute name="invisible" add="not my_field" separator="and" />
</page>
<group name="ship_to" position="attributes">
    <attribute name="invisible" add="my_direction == 'in'" separator="or" />
</group>
```
