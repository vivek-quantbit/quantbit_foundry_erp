# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance as stock_balance
from datetime import datetime

def getVal(val):
        return val if val is not None else 0

def ItemName(item_code):
	return frappe.get_value('Item', item_code , 'item_name')

def foundry_setting(company , field):
	return frappe.get_value('Foundry Setting', company , field)

class Pouring(Document):
	def calculate_total(self, child_table, total_field):
		return sum(getVal(i.get(total_field)) for i in self.get(child_table))

	def Get_Available_Stock(self, child_table , item_code_field , source_warehouse_field , available_stock_field , date = None):
		for d in self.get(child_table,filters = {item_code_field : ['!=', None] ,source_warehouse_field : ['!=', None]}):
			d.set(available_stock_field, stock_balance(d.get(item_code_field),d.get(source_warehouse_field),date))

	def Validate_Mandatory_Fields(self, fields):
		for d in fields:
			if not self.get(d):
				frappe.throw(f'Field {d} is Mandatory')

	def validate(self):
		self.Validate_Casting_Details()
		self.Validate_Charge_Mix()

	def before_save(self):
		self.Calculating_General_Details()

	def before_submite(self):
		pass

	@frappe.whitelist()
	def Calculating_General_Details(self):
		if self.heat_end_time and self.heat_start_time:
			self.total_heat_time = datetime.strptime(self.heat_end_time, "%H:%M:%S") - datetime.strptime(self.heat_start_time, "%H:%M:%S")
		if self.final_power_reading and self.initial_power_reading:
			self.total_power_consumed = self.final_power_reading - self.initial_power_reading
		if getVal(self.total_power_consumed) < 0:
			frappe.throw(title ="Power Reading Validation" , msg = f"'Total Power Consumption' Should not be negative")
			
	@frappe.whitelist()
	def get_casting_details_from_pattern(self):
		self.Validate_Mandatory_Fields(['company' , 'furnace'])

		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		for p in pattern_details:
			pattern_casting_details = frappe.get_doc("Pattern Master" , p.pattern_code)

			p.box_weight = pattern_casting_details.box_weight
			p.casting_weight = pattern_casting_details.casting_weight
			p.rr_weight = pattern_casting_details.rr_weight

			p.total_box_weight = p.box_weight * getVal(p.poured_boxes)
			p.total_casting_weight = p.casting_weight * getVal(p.poured_boxes)
			p.total_rr_weight = p.rr_weight * getVal(p.poured_boxes)

			for d in pattern_casting_details.pattern_master_casting_material_details :
				data_in = 	{
								'pattern_code': p.pattern_code,
								'casting_item_code': d.casting_item_code,
								'casting_item_name': ItemName(d.casting_item_code),
								'weight':d.weight,
								'uom':d.uom,
								'target_warehouse': foundry_setting(self.company ,'ft_warehouse'),
								'reference':d.name
							}

				data_check = self.get('casting_details' , filters= data_in)
				if not data_check:
					self.append("casting_details",data_in)

			if pattern_casting_details.pattern_grade_type and pattern_casting_details.pattern_grade:
				self.grade_type = pattern_casting_details.pattern_grade_type
				self.grade = pattern_casting_details.pattern_grade


	@frappe.whitelist()
	def Calculating_Casting_Details(self):
		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		for j in pattern_details:
			casting_details = self.get('casting_details' , filters = {'check': 1 ,'pattern_code': j.pattern_code})
			for i in casting_details:
				i.total_weight = i.quantity * i.weight
				i.total_rr_weight = (j.rr_weight/j.casting_weight)*(i.total_weight)

		self.total_casting_quantity = self.calculate_total('casting_details', 'quantity')
		self.total_casting_weight = self.calculate_total('casting_details', 'total_weight')
		self.total_rr_weight = self.calculate_total('casting_details', 'total_rr_weight')
		self.total_pouring_weight = self.total_casting_weight  +  self.total_rr_weight

		self.set_quantity_in_core_details()
		self.set_quantity_in_moulding_sand_details()
		self.set_amount_in_additional_cost_details()

	@frappe.whitelist()
	def set_quantity_in_casting_details(self):
		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		for p in pattern_details:
			cavity_type_list = []
			casting_details = self.get('casting_details' , filters = {'pattern_code': p.pattern_code, 'check': 1})
			for a in casting_details:
				cavity_type = frappe.get_value("Pattern Master Casting Material Details" ,{'casting_item_code': a.casting_item_code}, 'cavity_type')

				if cavity_type in cavity_type_list:
					for o in casting_details:
						o.quantity = o.total_rr_weight = o.total_weight = 0
				else:
					quantity_per_box = frappe.get_value("Pattern Master Cavity Details" , {'parent': p.pattern_code , 'cavity_type': cavity_type } , 'quantity_per_box')
					a.quantity = quantity_per_box * p.poured_boxes

				cavity_type_list.append(cavity_type)	
			
			cd = self.get('casting_details' , filters = {'pattern_code': p.pattern_code, 'check': 0})
			for d in cd:
				d.quantity = d.total_rr_weight = d.total_weight = 0

		self.Calculating_Casting_Details()
		self.set_quantity_in_charge_mix_details()
			
		
	def Validate_Casting_Details(self):
		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		for p in pattern_details:
			sum_casting_weight = 0
			casting_details = self.get('casting_details' , filters = {'pattern_code': p.pattern_code, 'check': 1})
			for a in casting_details:
				cavity_type = frappe.get_value("Pattern Master Casting Material Details" ,{'casting_item_code': a.casting_item_code}, 'cavity_type')
				quantity_per_box = frappe.get_value("Pattern Master Cavity Details" , {'parent': p.pattern_code , 'cavity_type': cavity_type } , 'quantity_per_box')
				quantity = quantity_per_box * p.poured_boxes
				total_casting_weight = quantity * a.weight
				if total_casting_weight < a.total_weight:
					frappe.throw(title ="Casting Details Validation" , msg = f"The maximum total casting weight of item {a.casting_item_code} must be '{total_casting_weight}' , you are entering casting quantity weighted '{a.total_weight}'")

				sum_casting_weight += a.total_weight
		
			if sum_casting_weight != p.total_casting_weight:
				frappe.throw(title ="Casting Details Validation" , msg = f"Total casting weight for pattern {p.pattern_code} should be '{p.total_casting_weight}' , you are entering casting quantity weighted '{sum_casting_weight}'")


	def set_quantity_in_charge_mix_details(self):
		if self.furnace and self.grade:
			grade_items_details = frappe.get_all("Grade Items Details", 
														filters = {"parent": self.grade},
														fields = ["item_code","percentage"] , order_by='idx ASC')
			source_warehouse =  foundry_setting(self.company ,'cms_warehouse')
			for d in grade_items_details :
					required_quantity = (d.percentage * self.furnace_capacity)/100

					data_in = 	{
									'raw_item_code': d.item_code,
									'raw_item_name': ItemName(d.item_code),
									'required_quantity': required_quantity,
								}

					data_check = self.get('charge_mix_details' , filters= data_in)
					if not data_check:
						self.append("charge_mix_details",	{
															'raw_item_code': d.item_code,
															'raw_item_name': ItemName(d.item_code),
															'required_quantity': required_quantity,
															'source_warehouse': source_warehouse,
															'available_stock': stock_balance(d.item_code,source_warehouse,self.heat_date) if (source_warehouse and d.item_code) else None,
														})
		else:
			frappe.throw(title ="Furnace & Grade Validation" , msg = f"Furnace and grade are must for entry")
	
	@frappe.whitelist()
	def Calculating_Charge_Mix(self):
		self.total_consumed_weight = self.calculate_total('charge_mix_details', 'used_quantity')
		self.Validate_Charge_Mix()

	def Validate_Charge_Mix(self):
		self.total_consumed_weight = self.calculate_total('charge_mix_details', 'used_quantity')
		furnace_capacity = self.furnace_capacity
		weight_percentage = foundry_setting(self.company , 'exceed_limit')
		remit_value = ((furnace_capacity * weight_percentage)/100)
		total_valid_quantity = furnace_capacity + remit_value

		if total_valid_quantity < self.total_consumed_weight:
			frappe.throw(title ="Charge Mix Validation" , msg =f'The Total Used Quantity of charge mix should be equal to {total_valid_quantity} which is Total Furnace Weight {furnace_capacity} + {weight_percentage}% remit value {remit_value}' )

	def set_quantity_in_core_details(self):
		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		source_warehouse =  foundry_setting(self.company ,'cs_warehouse')
		for p in pattern_details:
			casting_details = self.get('casting_details' , filters = {'pattern_code': p.pattern_code, 'check': 1 , 'casting_item_code': ['!=', None], 'quantity':['>',0]})
			for a in casting_details:
				core_details =frappe.get_all("Pattern Master Core Material Details", 
														filters = {"parent": p.pattern_code , 'casting_item_code' : a.casting_item_code},
														fields = ["core_item_code" , 'uom' , 'quantity'] , order_by='idx ASC')
				for d in core_details :
					required_quantity = d.quantity * a.quantity
					data_in = 	{
									'pattern_code': p.pattern_code,
									'casting_item_code': a.casting_item_code,
									'core_item_code': d.core_item_code,
									'required_quantity': required_quantity,
								}

					data_check = self.get('core_details' , filters= data_in)
					if not data_check:
						self.append("core_details",	{
															'pattern_code': p.pattern_code,
															'casting_item_code': a.casting_item_code,
															'core_item_code': d.core_item_code,
															'core_item_name': ItemName(d.core_item_code),
															'uom': d.uom,
															'required_quantity': required_quantity,
															'used_quantity':required_quantity,
															'source_warehouse': source_warehouse,
															'available_stock': stock_balance(d.core_item_code , source_warehouse , self.heat_date) if (source_warehouse and d.core_item_code) else None,
														})
		self.Calculating_Core_Details()

	@frappe.whitelist()
	def Calculating_Core_Details(self):
		self.total_core_quantity = self.calculate_total('core_details', 'used_quantity')

	def set_quantity_in_moulding_sand_details(self):
		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		source_warehouse =  foundry_setting(self.company ,'ms_warehouse')
		for p in pattern_details:
			moulding_sand_details =frappe.get_all("Pattern Master Moulding Sand Details", 
													filters = { "parent" : p.pattern_code ,"sand_item_code": ['not in' , [None ,'']],"quantity":['>',0]},
													fields = ["sand_item_code" , 'uom' , 'quantity'] , order_by='idx ASC')
			for d in moulding_sand_details :
				required_quantity = d.quantity * p.poured_boxes
				data_in = 	{
								'pattern_code': p.pattern_code,
								'sand_item_code': d.sand_item_code,
							}

				data_check = self.get('moulding_sand_details' , filters= data_in)
				if not data_check:
					self.append("moulding_sand_details",	{
													'pattern_code': p.pattern_code,
													'sand_item_code': d.sand_item_code,
													'sand_item_name': ItemName(d.sand_item_code),
													'uom': d.uom,
													'required_quantity': required_quantity,
													'used_quantity':required_quantity,
													'source_warehouse': source_warehouse,
													'available_stock': stock_balance(d.sand_item_code, source_warehouse , self.heat_date) if (source_warehouse and d.sand_item_code) else None,
												})

		self.Calculating_moulding_sand_details()

	@frappe.whitelist()
	def Calculating_moulding_sand_details(self):
		self.total_moulding_sand_quantity = self.calculate_total('moulding_sand_details', 'used_quantity')

	def set_amount_in_additional_cost_details(self):
		def set_additional_cost(company ,heat_date ,amount_child_table ,amount_parent , expense_account_field , amount_field ,check_field ,discription ,multiply_field):
			# frappe.throw(f'{amount_child_table}-{company}-{heat_date}-{amount_field}')
			amount_per_unit = frappe.get_value(amount_child_table,{"parent": company , "from_date" : ['<=',heat_date]},amount_field,order_by = "idx ASC")
			if not amount_per_unit:
				frappe.msgprint(f'Unable to set {discription} because of {amount_parent} not set for date {heat_date}')
			expense_head_account = frappe.get_value(amount_parent,company,expense_account_field)
			if amount_per_unit and expense_head_account:				
					data_in = 	{
									check_field: True,
								}
					data_check = self.get('additional_cost_details' , filters= data_in)
					if data_check:
						for k in data_check:
							k.amount = multiply_field * amount_per_unit
					else:
						self.append("additional_cost_details",	{
																	'discription': discription,
																	'expense_head_account': expense_head_account,
																	'amount': multiply_field * amount_per_unit,
																	check_field: True,
																})
		
		is_electricity_charges_applicable , is_labour_charges_applicable =  foundry_setting(self.company , ['is_electricity_charges_applicable' , 'is_labour_charges_applicable'])
		if is_electricity_charges_applicable:
			set_additional_cost(
								company = self.company , 
								heat_date = self.heat_date ,
								amount_child_table = "Foundry Power Consumption Details",
								amount_parent = "Foundry Power Consumption",
								expense_account_field = "expense_head_account",
								amount_field = 'amount_per_unit',
								check_field = 'is_electricity_expense',
								discription ="Electricity Expense",
								multiply_field = self.total_power_consumed,
								)
		
		if is_labour_charges_applicable:
			set_additional_cost(
								company = self.company , 
								heat_date = self.heat_date ,
								amount_child_table = "Foundry Setting Pouring Labour Charges Details",
								amount_parent = "Foundry Setting",
								expense_account_field = "expense_head_account",
								amount_field = 'amount_per_weight',
								check_field = 'is_labour_charges',
								discription ="Pouring Labour Charges",
								multiply_field = self.total_casting_weight,
								)


	@frappe.whitelist()
	def set_available_quantity_in_table(self):
		self.Get_Available_Stock('charge_mix_details' , 'raw_item_code' , 'source_warehouse' , 'available_stock' , self.heat_date)
		self.Get_Available_Stock('core_details' , 'core_item_code' , 'source_warehouse' , 'available_stock' , self.heat_date)
		self.Get_Available_Stock('moulding_sand_details' , 'sand_item_code' , 'source_warehouse' , 'available_stock' , self.heat_date)