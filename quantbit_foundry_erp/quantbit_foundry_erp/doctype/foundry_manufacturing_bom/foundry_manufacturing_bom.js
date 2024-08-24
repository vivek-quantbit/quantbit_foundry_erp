// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Foundry Manufacturing BOM", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Raw Material BOM Details', {
	check: function(frm) {
		frm.call({
			method:'get_quantity_per',
			doc:frm.doc
		})
	}
});

frappe.ui.form.on('Raw Material BOM Details', {
	percentage_input: function(frm) {
		frm.call({
			method:'get_quantity_per',
			doc:frm.doc
		})
	}
});

frappe.ui.form.on('Raw Material BOM Details', {
	qty: function(frm) {
		frm.call({
			method:'get_quantity_per',
			doc:frm.doc
		})
	}
});