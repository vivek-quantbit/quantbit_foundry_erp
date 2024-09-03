frappe.provide('frappe.custom');
// hello
frappe.custom.set_filters_for_doctype = function(doctype_name, frm) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Foundry Filter Setting DocType",
            filters: {
                "doctype_name": doctype_name
            },
            fields: ['name', "docfield_name", "docchild_name", "doclink_name"],
        },
        callback: async function(response) {
            if (response.message) {
                let data = response.message;
                data.forEach(async function(item) {
                    let field = item.docfield_name;
                    let child_field = item.docchild_name
                    let filter_arg
                    if (item.filterfield_field) {
                        filter_arg = frm.doc[item.filterfield_field];
                    } else {
                        filter_arg = item.filterfield_data;
                    }
                    let filter = await get_filter_list(frm, item.name, item.doclink_name);
                    if (child_field) {
                        frm.set_query(field, child_field, function() {
                            return {
                                filters: filter
                            };
                        });
                    } else {
                        frm.set_query(field, function() {
                            return {
                                filters: filter
                            };
                        });
                    }
                });
            }
        }
    });
};



async function get_filter_list(frm, filters_parent, doclink_name) {
    let filter_list = []
    const val = await frappe.db.get_doc("Foundry Filter Setting DocType", filters_parent)
    data = val.foundry_filter_setting_doctype_details
    data.forEach(function(item) {
        let filter_arg
        if (item.filterfield_field) {
            filter_arg = frm.doc[item.filterfield_field];
        } else {
            filter_arg = item.filterfield_data;
        }
        let filter = [doclink_name, item.filterfield_name, item.filterfield_type, filter_arg];
        filter_list.push(filter)

    });
    return filter_list;
}

// frappe.provide('frappe.custom');

// frappe.custom.set_filters_for_doctype = function(doctype_name, frm) {
//     frappe.call({
//         method: "frappe.client.get_list",
//         args: {
//             doctype: "Filter Setting DocType",
//             filters: { "doctype_name": doctype_name },
//             fields: ['name', "docfield_name", "docchild_name", "doclink_name", "filterfield_name", 'filterfield_type', 'filterfield_data', 'filterfield_field'],
//         },
//         callback: function(response) {
//             if (response.message) {
//                 let data = response.message;
//                 data.forEach(function(item) {
//                     let field = item.docfield_name;
//                     let child_field = item.docchild_name;

//                     let filter_arg;
//                     if (item.filterfield_field) {
//                         filter_arg = frm.doc[item.filterfield_field];
//                     } else {
//                         filter_arg = item.filterfield_data;
//                     }

//                     // Fetch filter list asynchronously and apply filters
//                     get_filter_list(item.name, item.doclink_name, function(filter_list) {
//                         if (child_field) {
//                             frm.set_query(field, child_field, function() { return { filters: filter_list }; });
//                         } else {
//                             frm.set_query(field, function() { return { filters: filter_list }; });
//                         }
//                     });
//                 });
//             }
//         }
//     });
// };

// function get_filter_list(filters_parent, doclink_name, callback) {
//     frappe.call({
//         method: "frappe.client.get_list",
//         args: {
//             doctype: "Foundry Filter Setting DocType Details",
//             filters: { "parent": filters_parent },
//             fields: ["filterfield_name", 'filterfield_type', 'filterfield_data', 'filterfield_field'],
//             ignore_permissions : 1
//         },
//         callback: function(response) {
//             let filter_list = [];
//             if (response.message) {
//                 let data = response.message;
                
//                 data.forEach(function(item) {
//                     let filter_arg;
//                     if (item.filterfield_field) {
//                         filter_arg = frm.doc[item.filterfield_field];
//                     } else {
//                         filter_arg = item.filterfield_data;
//                     }
//                     let filter = [doclink_name, item.filterfield_name, item.filterfield_type, filter_arg];
//                     filter_list.push(filter);
//                 });
//             }
//             // Invoke the callback function with filter_list after async call completes
//             if (callback) callback(filter_list);
//         }
//     });
// }
