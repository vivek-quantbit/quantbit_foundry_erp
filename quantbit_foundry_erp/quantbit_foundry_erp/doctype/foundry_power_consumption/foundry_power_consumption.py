# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FoundryPowerConsumption(Document):
	
	def before_save(self):
		eachpcd = sorted(self.get("power_consumption_details"), key=lambda x: x.from_date)
		for i in range(len(eachpcd)-1):
			eachpcd[i].to_date = eachpcd[i+1].from_date
		eachpcd[-1].to_date = "2100-01-01"
		
