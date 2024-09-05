# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatternMaster(Document):
	def validate(self):
		self.validation_data()


	@frappe.whitelist()
	def set_filters(self):
		final_listed =[]
		for d in self.get('pattern_master_casting_material_details'):
			final_listed.append(d.casting_item_code)
		return final_listed

	def validation_data(self , child_table=None , child_field = None , validate_from_field  = None , validating_attribute = None):
		for d in self.get("pattern_master_casting_treatment_details"):
			data = d.get('finished_source_warehouse')
			validation_data = frappe.get_value("Warehouse", data , "company")
			# frappe.throw(str(company))
			if self.company == validation_data:
				pass
			else:
				frappe.throw("frappe the invalida data")
		