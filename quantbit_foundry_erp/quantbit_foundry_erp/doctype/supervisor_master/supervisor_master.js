// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Supervisor Master", {
// 	refresh(frm) {

// 	},
// });

function set_filters_for_doctype(doctype_name ,frm)  {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Filter Setting DocType",
            filters: { "doctype_name": doctype_name },
            fields: ["docfield_name","docchild_name", "doclink_name", "filterfield_name", 'filterfield_type', 'filterfield_data' , 'filterfield_field'],
        },
        callback: function (response) {
            if (response.message) {
                let data = response.message;
                data.forEach(function (item) {
                    let field = item.docfield_name;
                    let child_field = item.docchild_name
                    let filter_arg
                    if(item.filterfield_field)
                        {
                            filter_arg = frm.doc[item.filterfield_field];
                        }
                    else
                        {
                            filter_arg = item.filterfield_data;
                        }


                    let filter = [[item.doclink_name, item.filterfield_name, item.filterfield_type, filter_arg]];
                    if(child_field)
                        {
                            frm.set_query(field,child_field, function() {return { filters: filter };});
                        }
                    else
                        {
                        frm.set_query(field, function () {return { filters: filter };});
                        }
                });
            }
        }
    });
};

frappe.ui.form.on('Supervisor Master', {
    setup: function (frm) {
        set_filters_for_doctype(frm.doctype, frm);
        
    },
    foundry_unit: function (frm) {
        set_filters_for_doctype(frm.doctype, frm);
        
    },
});