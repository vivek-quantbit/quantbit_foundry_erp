# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FoundryManufacturingBOM(Document):
	
	@frappe.whitelist()
	def get_quantity_per(self):
		total = sum((i.qty or 0) for i in self.get('raw_items') if i.check)
		percentage_items = [i for i in self.get('raw_items') if i.percentage_input]

		for i in percentage_items:
			i.qty = (i.percentage_input * total) / 100
