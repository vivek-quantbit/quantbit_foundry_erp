# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GradeMaster(Document):
	def validate(self):
		self.validate_percentage()
		self.validate_retain_items()
	
	def validate_percentage(self):
		grade_items_details = self.get("grade_items_details")
		total_percentage = 0.0
		for i in grade_items_details:
			if i.percentage :
				total_percentage = round(total_percentage,3) + round(i.percentage,3)

		if int(total_percentage) !=100 :
			frappe.throw(f'The addition of toal percentage must equal to 100 % the difference is {100- total_percentage}')

	def validate_retain_items(self):

		is_scrap_item = self.get("retained_items_details",filters = {'is_scrap_item':1})
		if len(is_scrap_item)>1:
			frappe.throw('"Retained Items Details" should only contain 1 "Is Scrap Item"')

		is_heal_metal = self.get("retained_items_details",filters = {'is_heal_metal':1})
		if len(is_heal_metal)>1:
			frappe.throw('"Retained Items Details" should only contain 1 "Is Heal Metal"')

		for d in self.get("retained_items_details"):
			if d.is_scrap_item and d.is_heal_metal:
				frappe.throw("One item should not be both 'Is Scrap Item' and 'Is Heal Metal'")