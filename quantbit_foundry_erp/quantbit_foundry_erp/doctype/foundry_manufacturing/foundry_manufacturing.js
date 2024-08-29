// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// ======================================================= Foundry Manufacturing ====================================================================

// after getting finished Item code Raw material for that finished item appended in child table Raw Items Details
frappe.ui.form.on('Foundry Manufacturing', {
	bom_reference: function(frm) {
		frm.clear_table("raw_items");
		frm.refresh_field('raw_items');
		frm.call({
			method:'get_raw_materials_from_connection',
			doc:frm.doc
		})
	},
	start_unit: function(frm) {
		frm.call({
			method:'calculating_power_consumption',
			doc:frm.doc
		})
	},
	end_unit: function(frm) {
		frm.call({
			method:'calculating_power_consumption',
			doc:frm.doc
		})
	},
	source_warehouse: function(frm) {
        frm.clear_table("raw_items");
        frm.refresh_field('raw_items');
        
        frm.call({
            method: 'get_bom_raw_materials',
            doc: frm.doc,
            callback: function(r) {
                if (r.success && frm.doc.source_warehouse) {
                    frm.doc.raw_items.forEach(function(item) {
                        item.source_warehouse = frm.doc.source_warehouse;
                    });
                    frm.refresh_field('raw_items');
                }
            }
        });
    },
	target_warehouse(frm) {
        if (frm.doc.target_warehouse) {
            frm.doc.finished_items.forEach(function(item) {
                item.target_warehouse = frm.doc.target_warehouse;
            });
            frm.refresh_field('finished_items');
        }
    }

});

// =================================================== Foundry Manufacturing Raw Material Details =======================================================

frappe.ui.form.on('Foundry Manufacturing Raw Material Details', {
	check: function(frm) {
		frm.call({
			method:'get_quantity_raw_items',
			doc:frm.doc
		})
		frm.refresh_field("raw_items")
	},
	source_warehouse: function(frm) {
		frm.call({
			method:'available_qty',
			doc:frm.doc
		})
	},
	item_code(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (frm.doc.source_warehouse) {
            frappe.model.set_value(cdt, cdn, 'source_warehouse', frm.doc.source_warehouse);
        }
        frm.refresh_field('raw_items');
    }
});

// ================================================ Foundry Manufacturing Scrap Details ===============================================================

frappe.ui.form.on('Foundry Manufacturing Scrap Details', {
	check: function(frm) {
		frm.call({
			method:'get_quantity_per',
			doc:frm.doc
		})
		frm.refresh_field("scrap_items")
	},
	percentage_input: function(frm) {
		frm.call({
			method:'get_quantity_per',
			doc:frm.doc
		})
		frm.refresh_field("scrap_items")
	},
	used_qty: function(frm) {
		frm.call({
			method:'get_quantity_per',
			doc:frm.doc
		})
		frm.refresh_field("scrap_items")
	}

});

// ================================================================================== Foundry Manufacturing Finished Item Details ================================================================================== 

frappe.ui.form.on("Foundry Manufacturing Finished Item Details", {
    finished_items_remove: function(frm, cdt, cdn) {
        frm.clear_table("raw_items");
		frm.refresh_field('raw_items');
		frm.call({
			method:'get_bom_raw_materials',
			doc:frm.doc
		})
    },
	ok_qty: function(frm) {
		frm.refresh_field('updated_quantity_to_manufacturing');
		frm.call({
			method:'calculate_total_quantity',
			doc:frm.doc
		})
	},
	rejected_qty: function(frm) {
		frm.refresh_field('updated_quantity_to_manufacturing');
		frm.call({
			method:'calculate_total_quantity',
			doc:frm.doc
		})
	},
	item_code: function(frm, cdt, cdn) {
        frm.clear_table("raw_items");
        frm.refresh_field('raw_items');
        frm.call({
            method: 'get_bom_raw_materials',
            doc: frm.doc
        });
        var child = locals[cdt][cdn];
        if (frm.doc.target_warehouse) {
            frappe.model.set_value(cdt, cdn, 'target_warehouse', frm.doc.target_warehouse);
        }
        frm.refresh_field('finished_items');
    },
	bom_reference: function(frm, cdt, cdn) {
        frm.clear_table("raw_items");
        frm.refresh_field('raw_items');
        frm.call({
            method: 'get_bom_raw_materials',
            doc: frm.doc
        });
    }

});
// =================================================== Filters ========================================================================================

//  filter warehouse based on company
frappe.ui.form.on("Foundry Manufacturing", {
	setup: function(frm) {
		frm.set_query("target_warehouse", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});

		frm.set_query("source_warehouse", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});
	}
});

//  filter warehouse based on company in child table component raw item
frappe.ui.form.on('Foundry Manufacturing', {
    refresh: function(frm) {
        frm.fields_dict['raw_items'].grid.get_field('source_warehouse').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                filters: [
                    ["Warehouse", "company", '=', frm.doc.company]
                ]
            };
        };
    }
});

//  filter Item based on company in child table component raw item
frappe.ui.form.on('Foundry Manufacturing', {
    refresh: function(frm) {
        frm.fields_dict['raw_items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "company", '=', frm.doc.company]
                ]
            };
        };
    }
});

// filter warehouse based on company in child table Foundry Manufacturing Scrap Details
frappe.ui.form.on('Foundry Manufacturing', {
    refresh: function(frm) {
        frm.fields_dict['scrap_items'].grid.get_field('source_warehouse').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                filters: [
                    ["Warehouse", "company", '=', frm.doc.company]
                ]
            };
        };
    }
});

//Finished Item group Details item group filters
frappe.ui.form.on('Foundry Manufacturing', {
	setup: function(frm) {
			frm.set_query("bom_reference", "finished_items", function(doc, cdt, cdn) {
				let d = locals[cdt][cdn];
				if(frm.doc.manufacturing_type && frm.doc.core_id){
					return {
						filters: [
							['Foundry Manufacturing BOM','manufacturing_type' ,"=" ,frm.doc.manufacturing_type],
							['Foundry Manufacturing BOM','core_id' ,"=" ,frm.doc.core_id]
							['Foundry Manufacturing BOM','enable','=', True]
						]
					};
				}
						
			})
	
    },
});
