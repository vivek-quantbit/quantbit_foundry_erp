# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.accounts.party  import get_party_details
from erpnext.stock.get_item_details import get_item_details
from frappe.model.mapper import get_mapped_doc
class OpenOrder(Document):
	
	#  Add supplier address
	@frappe.whitelist()
	def supplier_address(self,):
		if self.supplier_id and self.company:
			doc=get_party_details(company=self.company,party=self.supplier_id,party_type="Supplier",fetch_payment_terms_template=True,currency="INR",price_list="Standard Buying",posting_date=self.date,doctype="Purchase Order")
			self.party_name = doc.supplier
			self.address = doc.supplier_address
			self.supplier_gstin = doc.supplier_gstin
			self.gst_category = doc.gst_category
			self.address_display = doc.address_display
			self.company_address = doc.company_address
			self.shipping_address = doc.shipping_address
			self.shipping_address_display = doc.shipping_address_display
			self.billing_address = doc.billing_address
			self.billing_address_display = doc.billing_address_display
			self.company_gstin = doc.company_gstin
			self.place_of_supply = doc.place_of_supply
			self.purchase_template = doc.taxes_and_charges
			self.contact_display = doc.contact_display
			self.contact_email = doc.contact_email
			self.contact_mobile = doc.contact_mobile
			if doc.taxes:
				for i in doc.taxes:
					self.append("purchase_taxes",{
						"category":i.category,
						"add_deduct_tax":i.add_deduct_tax,
						"charge_type":i.charge_type,
						"included_in_print_rate":i.included_in_print_rate,
						"included_in_paid_amount":i.included_in_paid_amount,
						"account_head":i.account_head,
						"description":i.description,
						"rate":i.rate,
						"cost_center":i.cost_center,
						"account_currency":i.account_currency,
						"tax_amount":i.tax_amount,
						"tax_amount_after_discount_amount":i.tax_amount_after_discount_amount,
						"total":i.total,
						"base_tax_amount":i.base_tax_amount,
						"base_total":i.base_total,
						"base_tax_amount_after_discount_amount":i.base_tax_amount_after_discount_amount,	
						"item_wise_tax_detail":i.item_wise_tax_detail,
						
					})
					
	#  Add customer Address
	@frappe.whitelist()
	def customer_address(self):
		if self.customer and self.company:
			doc=get_party_details(company=self.company,party=self.customer,party_type="Customer",fetch_payment_terms_template=True,currency="INR",price_list="Standard Selling",posting_date=self.date,doctype="Sales Order")
			self.party_name = doc.customer
			self.address = doc.customer_address
			self.supplier_gstin = doc.supplier_gstin
			self.gst_category = doc.gst_category
			self.billing_address_gstin = doc.billing_address_gstin
			self.address_display = doc.address_display
			self.company_address = doc.company_address
			self.shipping_address = doc.shipping_address
			self.shipping_address_name = doc.shipping_address_name
			self.shipping_address_display = doc.shipping_address_display
			self.billing_address = doc.billing_address
			self.billing_address_display = doc.billing_address_display
			self.company_gstin = doc.company_gstin
			self.place_of_supply = doc.place_of_supply
			self.sales_template = doc.taxes_and_charges
			self.contact_display = doc.contact_display
			self.contact_email = doc.contact_email
			self.contact_mobile = doc.contact_mobile
			if doc.taxes:
				for i in doc.taxes:
					self.append("taxes",{
							"charge_type":i.charge_type,
							"account_head":i.account_head,
							"description":i.description,
							"included_in_print_rate":i.included_in_print_rate,
							"cost_center":i.cost_center,
							"rate":i.rate,
							"account_currency":i.account_currency,
							"tax_amount":i.tax_amount,
							"total":i.total,
							"tax_amount_after_discount_amount":i.tax_amount_after_discount_amount,
							"base_tax_amount":i.base_tax_amount,
							"base_total":i.base_total,
							"base_tax_amount_after_discount_amount":i.base_tax_amount_after_discount_amount,	
							"item_wise_tax_detail":i.item_wise_tax_detail,
							"dont_recompute_tax":i.dont_recompute_tax,
						})
				
	# To add tax template
	@frappe.whitelist()
	def item_tax_template(self):
		for i in self.get("items"):	
			child = get_item_details(args={"selling_price_list":"Standard Selling","company":self.company,"item_code": i.item_code, "customer": self.customer, "doctype": "Sales Order","currency":"INR"})
			i.item_tax_template = child.item_tax_template
			i.gst_rate = frappe.get_value("Item Tax Template",{"name":child.item_tax_template},"gst_rate")
			

	@frappe.whitelist()
	def call_two(self):
		self.calculate_tax()
		self.scalculate_tax()

	#  TO calculate tax in tax table for customer
	@frappe.whitelist()
	def calculate_tax(self):
		if self.customer:
			comp_state = frappe.get_value("Address", {"address_title": self.company}, 'state')
			supp_state = frappe.get_value("Address", {"address_title": self.customer}, 'state')
	
			tot_taxable_amount = 0 
			tot_amount = 0
		
			for i in self.get("items"):
				if i.rate:
					i.amount = i.rate * i.qty
					tot_amount += i.amount
				if comp_state == supp_state:
					i.cgst_rate = i.sgst_rate = (i.gst_rate / 2)
					i.cgst_amount = i.sgst_amount = round((i.amount / 100) * (i.cgst_rate), 2)
					i.taxable_value = i.cgst_amount + i.sgst_amount
					tot_taxable_amount += i.taxable_value
				else :
					i.igst_rate = i.gst_rate
					i.igst_amount = round((i.amount / 100) * (i.igst_rate), 2)
					i.taxable_value = i.igst_amount
					tot_taxable_amount += i.taxable_value

			if comp_state == supp_state:
				tot_taxable_amount = tot_taxable_amount/2
			else:
				tot_taxable_amount
			
			taxes_charges_doc = frappe.get_doc("Sales Taxes and Charges Template", self.sales_template)
			self.taxes = []
			for tx in taxes_charges_doc.taxes:
				tot_amount += tot_taxable_amount
				self.append("taxes", {
					"charge_type": tx.charge_type,
					"account_head": tx.account_head,
					"description": tx.description,
					"cost_center": tx.cost_center,
					"tax_amount": tot_taxable_amount,
					"total": round(tot_amount, 2)
				})
		
    
    #  TO calculate tax in tax table for supplier
	@frappe.whitelist()
	def scalculate_tax(self):
		if self.supplier_id:
			comp_state = frappe.get_value("Address", {"address_title": self.company}, 'state')
			supp_state = frappe.get_value("Address", {"address_title": self.supplier_id}, 'state')
	
			tot_taxable_amount = 0 
			tot_amount = 0
			for i in self.get("items"):
				if i.rate:
					i.amount = i.rate * i.qty
					tot_amount += i.amount
				if comp_state == supp_state:
					i.cgst_rate = i.sgst_rate = (i.gst_rate / 2)
					i.cgst_amount = i.sgst_amount = round((i.amount / 100) * (i.cgst_rate), 2)
					i.taxable_value = i.cgst_amount + i.sgst_amount
					tot_taxable_amount += i.taxable_value
				else :
					i.igst_rate = i.gst_rate
					i.igst_amount = round((i.amount / 100) * (i.igst_rate), 2)
					i.taxable_value = i.igst_amount
					tot_taxable_amount += i.taxable_value

			if comp_state == supp_state:
				tot_taxable_amount = tot_taxable_amount/2
			else:
				tot_taxable_amount

			taxes_charges_doc = frappe.get_doc("Purchase Taxes and Charges Template", self.purchase_template)
			self.taxes = []
			for tx in taxes_charges_doc.taxes:
				tot_amount += tot_taxable_amount
				self.append("purchase_taxes", {
					"charge_type": tx.charge_type,
					"account_head": tx.account_head,
					"description": tx.description,
					"cost_center": tx.cost_center,
					"tax_amount": tot_taxable_amount,
					"total": round(tot_amount, 2)
				})

#  To map data from open order to sales order
@frappe.whitelist()
def make_sales_order(source_name,target_doc = None):
	def set_missing_values(source,target):
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item_quantity(source,target,source_parent):
		target.qty = source.qty
		target.item_code = source.item_code

	doclist = get_mapped_doc(
		"Open Order",
				source_name,
		{
				"Open Order":{
					"doctype": "Sales Order",
				"field_map":{
								"customer":"customer",
								"sales_template":"taxes_and_charges",
								"po_no":"po_no",
								"po_date":"po_date"
							},
				},
				"Open Order Details":{
				"doctype":"Sales Order Item",
				"field_map":{
					"item_code":"item_code",
                    "item_name":"item_name",
                    "uom":"uom",
					"cgst_amount":"cgst_amount",
					"sgst_amount":"sgst_amount",
					"igst_amount":"igst_amount",
					"gst":"cgst_amount",
                    "qty":"qty",
                    "rate":"custom_open_order_rate",
                    "item_tax_template":"item_tax_template"
				},
				"postprocess":update_item_quantity,
				},
				"Open Order Sales Taxes and Charges":{
				"doctype":"Sales Taxes and Charges",
				"field_map":{
					"charge_type":"charge_type",
                    "account_head":"account_head",
                    "cost_center":"cost_center",
                    "tax_amount":"tax_amount",
                    "tax_amount":"base_tax_amount",
                    "total":"total"
				},
				},
			target_doc:
			set_missing_values,
		}
		)
	return doclist


#  To map data from open order to purchase order
@frappe.whitelist()
def make_purchase_order(source_name,target_doc = None):
	def set_missing_values(source,target):
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item_quantity(source,target,source_parent):
		target.qty = source.qty
		target.item_code = source.item_code

	doclist = get_mapped_doc(
		"Open Order",
				source_name,
		{
				"Open Order":{
					"doctype": "Purchase Order",
				"field_map":{
								"supplier_id":"supplier",
								"purchase_template":"taxes_and_charges"
							},
				},
				"Open Order Details":{
				"doctype":"Purchase Order Item",
				"field_map":{
					"item_code":"item_code",
                    "item_name":"item_name",
					"cgst_amount":"cgst_amount",
					"sgst_amount":"sgst_amount",
					"igst_amount":"igst_amount",
					"gst":"cgst_amount",
                    "qty":"qty",
                    "rate":"custom_open_order_rate",
                    "item_tax_template":"item_tax_template"
				},
				"postprocess":update_item_quantity,
				},
				"Open Order Purchase Taxes and Charges":{
				"doctype":"Purchase Taxes and Charges",
				"field_map":{
					"charge_type":"charge_type",
                    "account_head":"account_head",
                    "cost_center":"cost_center",
                    "tax_amount":"tax_amount",
                    "total":"total"
				},
				},
			target_doc:
			set_missing_values,
		}
		)
	return doclist