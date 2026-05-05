# Copyright (c) 2023, Nishant Shingate and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document
from frappe.utils import flt


def getVal(val):
	return val if val is not None else 0


def get_available_quantity(item_code, warehouse):
	result = frappe.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
	return result if result else 0


class Production(Document):
	@frappe.whitelist()
	def fill_row_operation_qty(self):
		settings = frappe.db.get_value("Machine Shop Setting", self.company, ["source_warehouse_p", "target_warehouse_p"], as_dict=True)
		for i in self.get("items"):
			i.target_warehouse = settings.target_warehouse_p
			raw_item = frappe.get_value("Item", i.item, "raw_material")
			item_name = frappe.get_value("Item", i.item, "item_name")
			self.append(
				"raw_items",
				{
					"item": i.item,
					"item_name": item_name,
					"raw_item": raw_item,
					"raw_item_name": frappe.get_value("Item", raw_item, "item_name"),
					"source_warehouse": settings.source_warehouse_p,
					"available_qty": get_available_quantity(raw_item, settings.source_warehouse_p),
					"required_time": 0.0,
				},
			)
			self.append(
				"item_operations",
				{
					"item": i.item,
					"finished_item_name": item_name,
				},
			)

	@frappe.whitelist()
	def append_cycle_time(self):
		self.set("qty_details", [])
		for v in self.get("item_operations"):
			v.cycle_time = 0
			v.boring = 0
			v.operation_rate = 0
			v.material_cycle_time = ""

			result = frappe.db.sql(
				"""
				SELECT
					mi.cycle_time,
					mi.boring,
					mi.operation_rate,
					mct.name,
					mi.source_warehouse,
					mi.target_warehouse,
					mi.raw_material
				FROM `tabMaterial Cycle Time` mct
				INNER JOIN `tabMachine Item` mi
					ON mi.parent = mct.name
				WHERE
					mct.item = %s
					AND mct.company = %s
					AND mct.from_date <= %s
					AND mi.operation = %s
				ORDER BY mct.from_date DESC
				LIMIT 1
				""",
				(v.item, self.company, self.date, v.operation),
				as_dict=True,
			)

			if result:
				r = result[0]
				v.cycle_time = flt(r.cycle_time)
				v.boring = flt(r.boring)
				v.operation_rate = flt(r.operation_rate)
				v.material_cycle_time = r.name

				source = r.source_warehouse
				target = r.target_warehouse
				raw = r.raw_material
				available_qty = get_available_quantity(raw, source) if raw and source else 0

				self.append(
					"qty_details",
					{
						"operation": v.operation,
						"cycle_time": v.cycle_time,
						"item": v.item,
						"machine": v.machine,
						"boring": v.boring,
						"source_warehouse": source,
						"target_warehouse": target,
						"raw_material": raw,
						"posting_date": self.date,
						"available_quantity": available_qty,
					},
				)

	stock_entries = []

	@frappe.whitelist()
	def get_od(self):
		pass

	@frappe.whitelist()
	def consumable_amount(self):
		for i in self.get("consumable_details"):
			i.amount = getVal(i.qty) * getVal(i.rate)

	def getRawItemName(self, itemName):
		for i in self.get("raw_items"):
			if i.item == itemName:
				return i.raw_item
		return ""

	def getRawItemQty(self, itemName):
		p = 0
		for i in self.get("qty_details"):
			if i.item == itemName:
				p = i.ok_qty
		return p if p else 0

	def getRawItemWareHouse(self, itemName):
		for i in self.get("raw_items"):
			if i.item == itemName:
				return i.source_warehouse
		return ""

	def getConsumables(self, itemName):
		consumables = []
		for i in self.get("consumable_details"):
			if i.finished_item == itemName:
				consumables.append(
					{
						"item_code": i.item if i.item is not None else "oil",
						"qty": i.qty,
						"s_warehouse": i.source_warehouse,
					}
				)
		return consumables

	def getToolings(self, itemName):
		toolings = []
		for i in self.get("tooling_details"):
			if i.finished_item == itemName:
				toolings.append(
					{
						"item_code": i.tooling_item if i.tooling_item is not None else "insert",
						"qty": i.qty,
						"s_warehouse": i.source_warehouse,
					}
				)
		return toolings

	# NOTE: The rest of the implementation from the provided script should be
	# migrated here as needed by the integration requirements.
