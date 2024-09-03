// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Grade Master", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('Grade Master', {
    setup: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
        
    },
});