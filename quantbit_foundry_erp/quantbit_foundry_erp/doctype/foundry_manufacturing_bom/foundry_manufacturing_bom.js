// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Foundry Manufacturing BOM", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Foundry Manufacturing BOM Raw Material Details', {
	check: function(frm) {
		frm.call({
			method:'get_quantity_per',
			doc:frm.doc
		})
	}
});

frappe.ui.form.on('Foundry Manufacturing BOM Raw Material Details', {
	percentage_input: function(frm) {
		frm.call({
			method:'get_quantity_per',
			doc:frm.doc
		})
	}
});

frappe.ui.form.on('Foundry Manufacturing BOM Raw Material Details', {
	qty: function(frm) {
		frm.call({
			method:'get_quantity_per',
			doc:frm.doc
		})
	}
});

frappe.ui.form.on('Foundry Manufacturing BOM', {
    setup: function(frm) {
        frm.set_query("item_code", function(doc) {
            if (frm.doc.item_group) {
                return {
                    filters: [
                        ['Item', 'item_group', '=', frm.doc.item_group],
                    ]
                };
            } else {
               
                return {};
            }
        });
    },
});