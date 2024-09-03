// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Foundry Filter Setting DocType", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Foundry Filter Setting DocType', {
    setup: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
        
    },
});