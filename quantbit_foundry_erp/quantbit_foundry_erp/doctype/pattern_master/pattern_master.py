# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatternMaster(Document):
	def validate(self):
		pass


	@frappe.whitelist()
	def set_filters(self):
		final_listed =[]
		for d in self.get('pattern_master_casting_material_details'):
			final_listed.append(d.casting_item_code)
		return final_listed
