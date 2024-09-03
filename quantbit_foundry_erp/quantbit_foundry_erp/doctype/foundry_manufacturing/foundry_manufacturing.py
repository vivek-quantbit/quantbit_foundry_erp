# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance as get_stock_balance

def gatevalue(value):
	return value if value else 1

def getval(value):
	return value if value else 0


class FoundryManufacturing(Document):
    
	# Fetch Child table from Foundry Manufacturing BOM doctype to Foundry Manufacturing Doctype
	@frappe.whitelist()
	def get_raw_materials_from_connection(self):
		if self.bom_reference:
			doc = frappe.get_doc('Foundry Manufacturing BOM', self.bom_reference)	
			if doc:
				self.item_group = doc.item_group
				self.core_name = doc.core_name
				self.append('finished_items',{
					'item_code':doc.item_code,
					'item_name':doc.item_name,
					'qty':doc.qty,
					'bom_reference':doc.name,
				})
				for d in doc.get("raw_items"):
					self.append('raw_items', {	
						"item_code": d.item_code,
						"item_name": d.item_name,
						"standard_qty":d.qty,
						"actual_qty":d.qty,
						"percentage_input":d.percentage_input,
						'reference_id': doc.name,
						"finished_item_name": doc.item_code,
						"uom": d.uom,
						"check":d.check,
					})				
			
	# After adding entry in finished item details child table
	@frappe.whitelist()
	def get_bom_raw_materials(self):
		for i in self.get("finished_items"):
			doc_name = frappe.get_value('Foundry Manufacturing BOM', {'item_code': i.item_code, "enable": True,"docstatus":1}, "name")
			if doc_name:
				doc = frappe.get_doc('Foundry Manufacturing BOM', doc_name)
				i.qty = doc.qty
				i.bom_reference = doc.name
				for d in doc.get("raw_items"):
					existing_entry = self.get_existing_entry(d.item_code)
					if existing_entry:
						existing_entry.standard_qty += float(d.qty)
						existing_entry.percentage_input += float(d.percentage_input)
					else:
						self.append('raw_items', {    
							"item_code": d.item_code,
							"item_name": d.item_name,
							"standard_qty": gatevalue(i.total_qty) * d.qty,
							"percentage_input": d.percentage_input,
							"uom": d.uom,
							"check": d.check,
							"source_warehouse":self.source_warehouse,
							"available_qty":get_stock_balance(d.item_code,self.source_warehouse,self.posting_date) if self.source_warehouse else 0.00,
							"finished_item_name": doc.item_code,
							'reference_id': i.name,
							'used_qty': getval(i.total_qty) * d.qty,
							'actual_qty': gatevalue(i.total_qty) * d.qty
						})
			if i.item_code and not doc_name:
				frappe.throw("Foundry Manufacturing BOM not found for item code")


	def get_existing_entry(self, item_code):
		for entry in self.raw_items:
			if entry.item_code == item_code:
				return entry
		return None


	# Calculate Available Quantity in source warehouse In Raw Items Details		
	@frappe.whitelist()
	def available_qty(self):
		for row in self.get("raw_items", {"item_code":["!=" , None],"source_warehouse":["!=" , None]}):
			row.available_qty = get_stock_balance(row.item_code,row.source_warehouse,self.posting_date)

	def _calculate_total(self, *values):
		return sum(value for value in values if value is not None)


	#Calculate total quantity depends on OK Quantity and Rejected Quantity in child table Finished Items Details
	@frappe.whitelist()
	def calculate_total_quantity(self):
		for i in self.get("finished_items"):
			i.total_qty = self._calculate_total(i.ok_qty, i.rejected_qty)
		self.qty_in_raw_details_from_finished_details()		

 
	# Calculate Standard Quantity and Used Quantity In Raw Item Details from child table ok and rejected qty			
	@frappe.whitelist()
	def qty_in_raw_details_from_finished_details(self):
		for row in self.get("raw_items"):
			quantity = 0
			for i in self.get("finished_items"):
				if i.bom_reference :
					quantity = quantity + ((getval(row.actual_qty) / getval(i.qty)) * getval(i.total_qty))
			row.standard_qty = quantity
			row.used_qty = quantity

    # calculating Unit consumption
	@frappe.whitelist()
	def calculating_power_consumption(self):
		if self.start_unit and  self.end_unit:
			self.unit_consumption = self.end_unit - self.start_unit
			if self.unit_consumption < 0 :
				frappe.throw("The 'Power Consumed' should not be negative")

	
	# get scrap quantity based on percentage input and checked Raw items details 
	@frappe.whitelist()
	def get_quantity_per(self):
		total = sum(i.used_qty for i in self.get('raw_items') if i.check)
		percentage_items = [i for i in self.get('scrap_items') if i.percentage_input]
		for i in percentage_items:
			i.used_qty = (i.percentage_input * total) / 100


	# calculate used quantity depends on percentage input in Raw items Details and scrap items child table 
	@frappe.whitelist()
	def get_quantity_raw_items(self):
		total = sum(i.actual_qty for i in self.get('raw_items') if i.check)
		percentage_items = [i for i in self.get('raw_items') if i.percentage_input]
		for i in percentage_items:
			i.used_qty = (i.percentage_input * total) / 100
   
	def on_submit(self):
		self.Manufacturing_stock_entry()
		self.mi_stock_entry_scrap_details()


	# After Submitting Foundry Manufacturing Stock Entry will be created 
	@frappe.whitelist()
	def Manufacturing_stock_entry(self):
		total = sum(i.total_qty for i in self.get('finished_items') if i.total_qty)
		if total == 0:
			frappe.throw("Total quantity cannot be zero.")
		for f in self.get("finished_items"):
			doc = frappe.new_doc("Stock Entry")
			doc.stock_entry_type = "Foundry Manufacturing"
			doc.company = self.company
			doc.set_posting_time = True
			doc.posting_date =self.posting_date
			doc.from_warehouse = self.source_warehouse
			doc.append("items", {
				"item_code": f.item_code,
				"qty": f.ok_qty,
				"t_warehouse": f.target_warehouse,
				"is_finished_item": True,
			})
			
			for i in self.get("raw_items"):	
				doc.append("items", {
					"s_warehouse": i.source_warehouse,
					"item_code": i.item_code,
					"item_name": i.item_name,
					"qty": (f.total_qty * (i.actual_qty*f.ok_qty))/total ,
				})
			
			for j in self.get("additional_costs"):
				doc.append("additional_costs", {
					"expense_account": j.expense_account,
					"description": j.description,
					"amount":(f.total_qty *  j.amount )/total,
				})
			doc.custom_foundry_manufacturing = self.name
			doc.insert()
			doc.save()
			doc.submit()

	# After Submitting Foundry Manufacturing Material Issue Stock Entry of Scrap Information will be created 
	@frappe.whitelist()
	def mi_stock_entry_scrap_details(self):
		total = sum(i.total_qty for i in self.get('finished_items') if i.total_qty)
		if total == 0:
			frappe.throw("Total quantity cannot be zero.")
        
		for f in self.get("finished_items",{"rejected_qty": [">", 0]}):
			doc = frappe.new_doc("Stock Entry")
			doc.stock_entry_type = "Foundry Manufacturing Issue"
			doc.company = self.company
			doc.set_posting_time = True
			doc.posting_date =self.posting_date
			doc.from_warehouse = self.source_warehouse
			for i in self.get("raw_items"):	
				doc.append("items", {
					"s_warehouse": i.source_warehouse,
					"item_code": i.item_code,
					"item_name": i.item_name,
					"qty": (f.total_qty *  (i.actual_qty* f.rejected_qty))/total ,
				})
			doc.custom_foundry_manufacturing = self.name
			doc.insert()
			doc.save()
			doc.submit() 