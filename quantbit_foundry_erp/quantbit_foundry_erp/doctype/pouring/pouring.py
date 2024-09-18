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

class Pouring(Document):
	def foundry_setting(self,field):
		return frappe.get_value('Foundry Setting', self.company , field)

	def calculate_total(self, child_table, total_field):
		return sum(getVal(i.get(total_field)) for i in self.get(child_table))

	def Get_Available_Stock(self, child_table , item_code_field , source_warehouse_field , available_stock_field , date = None):
		for d in self.get(child_table,filters = {item_code_field : ['!=', None] ,source_warehouse_field : ['!=', None]}):
			d.set(available_stock_field, stock_balance(d.get(item_code_field),d.get(source_warehouse_field),date))

	def Validate_Mandatory_Fields(self, fields):
		for d in fields:
			if not self.get(d):
				field_lable = frappe.get_value("DocField" ,{'parent': 'Pouring' , 'fieldname':d},'label')
				frappe.throw(f'Field "{field_lable}" is Mandatory')

	def validate(self):
		self.Validate_Casting_Details()
		self.Validate_Charge_Mix()

	def before_save(self):
		self.Calculating_General_Details()
		self.set_amount_in_additional_cost_details()
		

	def before_submit(self):
		pass

	@frappe.whitelist()
	def Calculating_General_Details(self):
		if self.heat_end_time and self.heat_start_time:
			self.total_heat_time = str(datetime.strptime(self.heat_end_time, "%H:%M:%S") - datetime.strptime(self.heat_start_time, "%H:%M:%S"))
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
								'target_warehouse': self.foundry_setting('ft_warehouse'),
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
		self.set_quantity_in_additional_consumable_details()
		self.set_amount_in_additional_cost_details()
		self.set_quantity_in_retained_items_details()

	@frappe.whitelist()
	def set_quantity_in_casting_details(self):
		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		for p in pattern_details:
			cavity_type_list = []
			casting_details = self.get('casting_details' , filters = {'pattern_code': p.pattern_code, 'check': 1})
			for a in casting_details:
				cavity_type = frappe.get_value("Pattern Master Casting Material Details" ,{'parent': p.pattern_code,'casting_item_code': a.casting_item_code}, 'cavity_type')

				if cavity_type in cavity_type_list:
					for o in casting_details:
						o.quantity = o.total_rr_weight = o.total_weight = 0
				else:
					quantity_per_box = frappe.get_value("Pattern Master Cavity Details" , {'parent': p.pattern_code , 'cavity_type': cavity_type } , 'quantity_per_box')
					a.quantity = getVal(quantity_per_box) * p.poured_boxes

				cavity_type_list.append(cavity_type)	
			
			cd = self.get('casting_details' , filters = {'pattern_code': p.pattern_code, 'check': 0})
			for d in cd:
				d.quantity = d.total_rr_weight = d.total_weight = 0

		self.Calculating_Casting_Details()
		self.set_quantity_in_charge_mix_details()
			
		
	def Validate_Casting_Details(self):
		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		for p in pattern_details:
			max_qty = 0
			item_list = frappe.db.sql("""
										SELECT pmc.cavity_type , pmc.quantity_per_box , GROUP_CONCAT(pmcmd.casting_item_code) as item_list
										FROM `tabPattern Master` pm
										INNER JOIN `tabPattern Master Cavity Details` pmc ON pm.name = pmc.parent
										INNER JOIN `tabPattern Master Casting Material Details` pmcmd ON pm.name = pmcmd.parent AND pmc.cavity_type = pmcmd.cavity_type
										WHERE pm.name = '{0}'
										GROUP BY pmc.cavity_type
									""".format(p.pattern_code), as_dict=True)
			for i in item_list:
				max_qty = i.quantity_per_box * p.poured_boxes
				casting_details = self.get('casting_details' , filters = {'pattern_code': p.pattern_code,'check': 1 , 'casting_item_code': ['in', i.item_list]})
				total_quantity = 0
				for j in casting_details:
					total_quantity += j.quantity
				if max_qty < total_quantity:
					frappe.throw(f'The maximum combine quantity you can set of items {i.item_list} of pattern code {p.pattern_code} is {max_qty}, you are entering {total_quantity} combine quantity')
						

	def set_quantity_in_charge_mix_details(self):
		if self.furnace and self.grade:
			grade_items_details = frappe.get_all("Grade Items Details", 
														filters = {"parent": self.grade},
														fields = ["item_code","percentage"] , order_by='idx ASC')
			source_warehouse =  self.foundry_setting('cms_warehouse')
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
		weight_percentage = self.foundry_setting('exceed_limit')
		remit_value = ((furnace_capacity * getVal(weight_percentage))/100)
		total_valid_quantity = furnace_capacity + remit_value

		if total_valid_quantity < self.total_consumed_weight:
			frappe.throw(title ="Charge Mix Validation" , msg =f'The Total Used Quantity of charge mix should be equal to {total_valid_quantity} which is Total Furnace Weight {furnace_capacity} + {weight_percentage}% remit value {remit_value}' )

	def set_quantity_in_core_details(self):
		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		source_warehouse =  self.foundry_setting('cs_warehouse')
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
		source_warehouse =  self.foundry_setting('ms_warehouse')
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

	def set_quantity_in_additional_consumable_details(self):
		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
		source_warehouse =  self.foundry_setting('acs_warehouse')
		for p in pattern_details:
			additional_consumable_details =frappe.get_all("Pattern Master Additional Consumable Details", 
													filters = { "parent" : p.pattern_code ,"consumable_item_code": ['not in' , [None ,'']],"quantity":['>',0]},
													fields = ["consumable_item_code" , 'uom' , 'quantity'] , order_by='idx ASC')
			for d in additional_consumable_details :
				required_quantity = d.quantity * p.poured_boxes
				data_in = 	{
								'pattern_code': p.pattern_code,
								'consumable_item_code': d.consumable_item_code,
							}

				data_check = self.get('additional_consumable_details' , filters= data_in)
				if not data_check:
					self.append("additional_consumable_details",	{
													'pattern_code': p.pattern_code,
													'consumable_item_code': d.consumable_item_code,
													'consumable_item_name': ItemName(d.consumable_item_code),
													'uom': d.uom,
													'required_quantity': required_quantity,
													'used_quantity':required_quantity,
													'source_warehouse': source_warehouse,
													'available_stock': stock_balance(d.consumable_item_code, source_warehouse , self.heat_date) if (source_warehouse and d.consumable_item_code) else None,
												})

		self.Calculating_additional_consumable_details()

	@frappe.whitelist()
	def Calculating_additional_consumable_details(self):
		self.total_additional_consumable_quantity = self.calculate_total('additional_consumable_details', 'used_quantity')

	def set_quantity_in_retained_items_details(self):
		self.Validate_Mandatory_Fields(['grade'])
		grade_data = frappe.get_all("Grade Master Retained Items Details", filters = {'parent' : self.grade} , fields =['retained_item_code','is_scrap_item','is_heal_metal'] , order_by='idx ASC')
		total_rr_weight = getVal(self.total_rr_weight)

		for g in grade_data:
			quantity = 0
			target_warehouse = None
			if g.is_scrap_item:
				quantity = total_rr_weight
				target_warehouse = self.foundry_setting('st_warehouse')
			if g.is_heal_metal:
				target_warehouse = self.foundry_setting('ht_warehouse')
			data_in = 	{
							'retained_item_code': g.retained_item_code,
					}

			data_check = self.get('retained_items_details' , filters= data_in)
			if data_check:
				if g.is_scrap_item:
					for i in data_check:
						i.quantity = quantity
			else:
				self.append("retained_items_details",	{
												'retained_item_code': g.retained_item_code,
												'retained_item_name': g.retained_item_name,
												'target_warehouse': target_warehouse,
												'quantity':quantity
											})

	def set_amount_in_additional_cost_details(self):

		def set_additional_cost(multiply_by , amount_per_unit , expense_head_account ,  additional_cost_type ):
			amount = getVal(multiply_by) * getVal(amount_per_unit)
			if amount:
				data_in = 	{
								'additional_cost_type': additional_cost_type,
							}
				data_check = self.get('additional_cost_details' , filters= data_in)
				if data_check:
					pass
				else:
					self.append("additional_cost_details",	{
																'discription': additional_cost_type,
																'expense_head_account': expense_head_account,
																'amount': amount,
																'additional_cost_type': additional_cost_type,
															})

		self.Validate_Mandatory_Fields(['company', 'heat_date'])
		foundry_additional_cost = frappe.get_all("Foundry Additional Cost", filters = {'company':self.company,'is_enable':1},fields = ["name" , 'expense_head_account' , 'foundry_additional_cost_type'])
		for f in foundry_additional_cost:
			amount_per_unit , wise = frappe.get_value('Foundry Additional Cost Details',{"parent": f.name , "from_date" : ['<=',self.heat_date]},['amount','wise'])
			expense_head_account = f.expense_head_account
			foundry_additional_cost_type = f.foundry_additional_cost_type
			
			if wise == 'Unit':
				is_power_consumption = frappe.get_value("Foundry Additional Cost Type",f.foundry_additional_cost_type , 'is_power_consumption')
				if is_power_consumption:
					multiply_by = getVal(self.total_power_consumed)
				else :
					multiply_by = self.total_casting_quantity
			elif wise == 'Weight':
				multiply_by = getVal(self.total_casting_weight)
			else:
				self.Validate_Mandatory_Fields(['total_heat_time'])
				total_sec = sum(int(x) * 60 ** i for i, x in enumerate(reversed(self.total_heat_time.split(':'))))
				multiply_by = total_sec / 3600

			set_additional_cost(multiply_by = multiply_by ,amount_per_unit = amount_per_unit, expense_head_account = expense_head_account, additional_cost_type = foundry_additional_cost_type)


	@frappe.whitelist()
	def set_available_quantity_in_table(self):
		self.Get_Available_Stock('charge_mix_details' , 'raw_item_code' , 'source_warehouse' , 'available_stock' , self.heat_date)
		self.Get_Available_Stock('core_details' , 'core_item_code' , 'source_warehouse' , 'available_stock' , self.heat_date)
		self.Get_Available_Stock('moulding_sand_details' , 'sand_item_code' , 'source_warehouse' , 'available_stock' , self.heat_date)
		self.Get_Available_Stock('additional_consumable_details' , 'consumable_item_code' , 'source_warehouse' , 'available_stock' , self.heat_date)