// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Pattern Master", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Pattern Master', {
    setup: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
        set_filters_for_casting_items(frm);
    },
    company: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
    },
    pattern_grade_type: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
    },
    pattern_grade: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
    },
    pattern_master_casting_material_details_remove: function (frm) {
        set_filters_for_casting_items(frm);
    },
});

frappe.ui.form.on('Pattern Master Casting Material Details', {
    casting_item_code: function(frm) {
        set_filters_for_casting_items(frm);
    },
    pattern_master_casting_material_details_remove: function (frm) {
        set_filters_for_casting_items(frm);
    },
});

function set_filters_for_casting_items(frm) {
    frappe.call({
        method: 'set_filters',
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                var k = r.message;

                frm.set_query("casting_item_code", "pattern_master_core_material_details", function(doc, cdt, cdn) {
                    let d = locals[cdt][cdn];
                    return {
                        filters: [
                            ['Item', 'name', 'in', k],
                        ]
                    };
                });

                frm.set_query("casting_item_code", "pattern_master_casting_treatment_details", function(doc, cdt, cdn) {
                    let d = locals[cdt][cdn];
                    return {
                        filters: [
                            ['Item', 'name', 'in', k],
                        ]
                    };
                });
            }
        }
    });
}
