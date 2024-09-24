# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FoundrySetting(Document):

	def validate(self):
		pass

	def before_save(self):
		pass