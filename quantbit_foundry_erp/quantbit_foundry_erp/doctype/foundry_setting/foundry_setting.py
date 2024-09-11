# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FoundrySetting(Document):

	def validate(self):
		self.Validate_electricity_charges_applicable()

	def before_save(self):
		eachpcd = sorted(self.get("pouring_labour_charges_details"), key=lambda x: x.from_date)
		for i in range(len(eachpcd)-1):
			eachpcd[i].to_date = eachpcd[i+1].from_date
		eachpcd[-1].to_date = "2100-01-01"

	def Validate_electricity_charges_applicable(self):
		if self.is_electricity_charges_applicable:
			power_consumption = frappe.get_all("Foundry Power Consumption Details",filters = {"parent": self.company },)
			if not power_consumption:
				frappe.throw(title ="Power Consumption Validation" , msg = f"Please fill 'Foundry Power Consumption' to apply power consumption charges on pouring")