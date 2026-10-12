# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import Form, TransactionCase


class TestPartnerProratedProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Template = cls.env["product.template"]
        classification = cls.env["product.equipment.classification"].create(
            {"name": "人工呼吸器", "code": "80"}
        )
        cls.ventilator = Template.create(
            {
                "name": "人工呼吸器",
                "product_kind": "equipment",
                "equipment_classification_id": classification.id,
            }
        )
        cls.concentrator = Template.create(
            {
                "name": "酸素濃縮器",
                "product_kind": "equipment",
                "equipment_classification_id": classification.id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "病院A", "prorated_billing": True}
        )

    def test_not_prorated_at_all_without_the_switch(self):
        self.partner.prorated_billing = False
        self.partner.prorated_product_tmpl_ids = self.ventilator
        self.assertFalse(self.partner._is_prorated_for_equipment(self.ventilator))

    def test_an_empty_list_means_every_rental(self):
        self.assertTrue(self.partner._is_prorated_for_equipment(self.ventilator))
        self.assertTrue(self.partner._is_prorated_for_equipment(self.concentrator))
        # A fee that bills no equipment at all follows the customer switch.
        self.assertTrue(
            self.partner._is_prorated_for_equipment(self.env["product.template"])
        )

    def test_a_list_narrows_it_to_that_equipment(self):
        self.partner.prorated_product_tmpl_ids = self.ventilator
        self.assertTrue(self.partner._is_prorated_for_equipment(self.ventilator))
        self.assertFalse(self.partner._is_prorated_for_equipment(self.concentrator))
        self.assertFalse(
            self.partner._is_prorated_for_equipment(self.env["product.template"])
        )

    def test_a_set_is_prorated_when_any_of_its_equipment_is(self):
        self.partner.prorated_product_tmpl_ids = self.ventilator
        self.assertTrue(
            self.partner._is_prorated_for_equipment(self.ventilator | self.concentrator)
        )

    def test_a_contact_carries_its_company_list(self):
        self.partner.is_company = True
        self.partner.prorated_product_tmpl_ids = self.ventilator
        contact = self.env["res.partner"].create(
            {"name": "請求先担当", "parent_id": self.partner.id, "type": "invoice"}
        )
        self.assertEqual(contact.prorated_product_tmpl_ids, self.ventilator)
        self.assertTrue(contact._is_prorated_for_equipment(self.ventilator))
        self.assertFalse(contact._is_prorated_for_equipment(self.concentrator))
        # Synced downward only, so the contact cannot keep a list of its own.
        with Form(contact) as form:
            self.assertTrue(form._get_modifier("prorated_product_tmpl_ids", "readonly"))
