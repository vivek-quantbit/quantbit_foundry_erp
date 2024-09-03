// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Supervisor Master", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Supervisor Master', {
    setup: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
        
    },
    foundry_unit: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
        
    },
});
