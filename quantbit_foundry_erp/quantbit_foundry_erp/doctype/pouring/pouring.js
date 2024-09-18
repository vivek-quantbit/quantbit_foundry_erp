// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Pouring", {
// 	refresh(frm) {

// 	},
// });
function method_call(frm, method, list_of_table_remove = null) {
    list_of_table_remove = list_of_table_remove || [];
    list_of_table_remove.forEach(function(table_name) {
        frm.clear_table(table_name);
        frm.refresh_field(table_name);
    });
    frm.call({
        method: method,
        doc: frm.doc,
    });
}

frappe.ui.form.on('Pouring', {
    setup: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
    },
    is_sales_order_applicable: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
    },
    pattern_details_remove: function (frm) {
        method_call(frm,'get_casting_details_from_pattern',['casting_details'])
    },
    heat_end_time: function (frm) {
        method_call(frm,'Calculating_General_Details')
    },
    heat_start_time: function (frm) {
        method_call(frm,'Calculating_General_Details')
    },
    final_power_reading: function (frm) {
        method_call(frm,'Calculating_General_Details')
    },
    initial_power_reading: function (frm) {
        method_call(frm,'Calculating_General_Details')
    },

    
});

frappe.ui.form.on('Pouring Pattern Details', {
    pattern_code: function (frm) {
        method_call(frm,'get_casting_details_from_pattern',['casting_details','core_details' , 'moulding_sand_details','additional_consumable_details','additional_cost_details'])
    },
    poured_boxes: function (frm) {
        method_call(frm,'get_casting_details_from_pattern',['casting_details','core_details' , 'moulding_sand_details','additional_consumable_details','additional_cost_details'])
    },
    pattern_details_remove: function (frm) {
        method_call(frm,'get_casting_details_from_pattern',['casting_details','core_details' , 'moulding_sand_details','additional_consumable_details','additional_cost_details'])
    }
});

frappe.ui.form.on('Pouring Casting Details', {
    check: function (frm) {
        method_call(frm,'set_quantity_in_casting_details',['core_details' , 'moulding_sand_details','additional_consumable_details','additional_cost_details'])
    },
    quantity: function (frm) {
        method_call(frm,'Calculating_Casting_Details',['core_details' , 'moulding_sand_details','additional_consumable_details','additional_cost_details'])
    }
});

frappe.ui.form.on('Pouring Charge Mix Details', {
    raw_item_code: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    source_warehouse: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    used_quantity: function (frm) {
        method_call(frm,'Calculating_Charge_Mix')
    },
});

frappe.ui.form.on('Pouring Core Details', {
    core_item_code: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    source_warehouse: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    used_quantity: function (frm) {
        method_call(frm,'Calculating_Core_Details')
    },
});

frappe.ui.form.on('Pouring Moulding Sand Details', {
    sand_item_code: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    source_warehouse: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    used_quantity: function (frm) {
        method_call(frm,'Calculating_moulding_sand_details')
    },
});

frappe.ui.form.on('Pouring Additional Consumable Details', {
    consumable_item_code: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    source_warehouse: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    used_quantity: function (frm) {
        method_call(frm,'Calculating_additional_consumable_details')
    },
});

// def Validate_Casting_Details(self):
// 		pattern_details = self.get("pattern_details", filters = {'pattern_code':['!=', None] , 'poured_boxes': ['not in', [None , 0]]})
// 		for p in pattern_details:
// 			sum_casting_weight = 0
// 			casting_details = self.get('casting_details' , filters = {'pattern_code': p.pattern_code, 'check': 1})
// 			for a in casting_details:
// 				cavity_type = frappe.get_value("Pattern Master Casting Material Details" ,{'parent': p.pattern_code,'casting_item_code': a.casting_item_code}, 'cavity_type')
// 				quantity_per_box = frappe.get_value("Pattern Master Cavity Details" , {'parent': p.pattern_code , 'cavity_type': cavity_type } , 'quantity_per_box')
// 				quantity = quantity_per_box * p.poured_boxes
// 				total_casting_weight = quantity * a.weight
// 				if total_casting_weight < a.total_weight:
// 					frappe.throw(title ="Casting Details Validation" , msg = f"The maximum total casting weight of item {a.casting_item_code} must be '{total_casting_weight}' , you are entering casting quantity weighted '{a.total_weight}'")

// 				sum_casting_weight += a.total_weight
		
// 			if sum_casting_weight != p.total_casting_weight:
// 				frappe.throw(title ="Casting Details Validation" , msg = f"Total casting weight for pattern {p.pattern_code} should be '{p.total_casting_weight}' , you are entering casting quantity weighted '{sum_casting_weight}'")