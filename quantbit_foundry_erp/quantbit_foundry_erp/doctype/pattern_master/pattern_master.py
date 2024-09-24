# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatternMaster(Document):
	def validate(self):
		self.Calculate_RR_Weight()
		self.validation_data()

	def before_save(self):
		pass

	@frappe.whitelist()
	def set_filters(self):
		final_listed =[]
		for d in self.get('pattern_master_casting_material_details'):
			final_listed.append(d.casting_item_code)
		return final_listed

	@frappe.whitelist()
	def Calculate_RR_Weight(self):
		total_casting_weight = 0
		for j in self.get("pattern_master_cavity_details"):
			weight = 0
			for i in self.get("pattern_master_casting_material_details", filters={"cavity_type": j.cavity_type}):
				weight = i.weight
			total_casting_item_weight = weight * j.quantity_per_box
			total_casting_weight += total_casting_item_weight

		self.casting_weight = total_casting_weight
		self.rr_weight = self.box_weight - total_casting_weight

	def validation_data(self):
		for j in self.get("pattern_master_cavity_details"):
			weights = set()
			for i in self.get("pattern_master_casting_material_details", filters={"cavity_type": j.cavity_type}):
				weights.add(i.weight)
			if len(weights) > 1:
				frappe.throw(f"Cavity type '{j.cavity_type}' has multiple weights")
		
		if self.rr_weight < 0:
			frappe.throw(title ="Runner & Riser Weight should not be 0 " , msg = f"Total Box Weight : {self.box_weight} ,Total Casting Weight : {self.casting_weight} , Runner & Riser Weight : {self.rr_weight}")


		for k in self.get("pattern_master_casting_material_details"):
			if len(self.get("pattern_master_cavity_details" ,filters={"cavity_type": k.cavity_type})) == 0:
				frappe.throw(title ="Pattern Master Casting Material Details Validation" , msg =f"Please define '{k.cavity_type}' Cavity Type in 'Pattern Master Cavity Details'")
