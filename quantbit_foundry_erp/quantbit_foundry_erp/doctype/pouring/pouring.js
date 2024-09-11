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
        method_call(frm,'get_casting_details_from_pattern',['casting_details'])
    },
    poured_boxes: function (frm) {
        method_call(frm,'get_casting_details_from_pattern',['casting_details'])
    },
    pattern_details_remove: function (frm) {
        method_call(frm,'get_casting_details_from_pattern',['casting_details'])
    }
});

frappe.ui.form.on('Pouring Casting Details', {
    check: function (frm) {
        method_call(frm,'set_quantity_in_casting_details',['core_details' , 'moulding_sand_details'])
    },
    quantity: function (frm) {
        method_call(frm,'Calculating_Casting_Details',['core_details' , 'moulding_sand_details'])
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
    core_item_code: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    source_warehouse: function (frm) {
        method_call(frm,'set_available_quantity_in_table')
    },
    used_quantity: function (frm) {
        method_call(frm,'Calculating_moulding_sand_details')
    },
});
