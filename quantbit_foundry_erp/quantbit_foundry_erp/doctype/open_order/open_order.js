// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt

//  ============================================================= Filter ===================================================================================
frappe.ui.form.on("Open Order", {
    setup: function(frm) {
        console.log("hello")
        frm.set_query("sales_template", function() { 
            return {
                filters: [
                    ["Sales Taxes and Charges Template", "company", '=', frm.doc.company]
                ]
            };
        });

    }
});
frappe.ui.form.on("Open Order", {
    setup: function(frm) {
        frm.set_query("purchase_template", function() {
            return {
                filters: [
                    ["Purchase Taxes and Charges Template", "company", '=', frm.doc.company]
                ]
            };
        });
        
    }
});
frappe.ui.form.on('Open Order', {
    setup: function(frm) {
        frm.set_query("item_code", "items", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "company", '=', frm.doc.company]
                ]   
            };
        });
    }
});

frappe.ui.form.on('Open Order', {
    setup: function(frm) {
        frm.set_query("item_tax_template", "items", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item Tax Template", "company", '=', frm.doc.company]
                ]   
            };
        });
    }
});

// ======================================================== Open Order ===================================================================================

frappe.ui.form.on('Open Order', {
	supplier_id: function(frm) {
        frm.clear_table("purchase_taxes");
        frm.refresh_field('purchase_taxes');
        
        frm.call({
            method: 'supplier_address',
            doc: frm.doc,
        })

    },
	customer: function(frm) {
        frm.clear_table("taxes");
        frm.refresh_field('taxes');
        frm.call({
            method: 'customer_address',
            doc: frm.doc,
        })

    },
});
 
// ========================================================= Open Order Details ============================================================================
frappe.ui.form.on('Open Order Details', {
    item_code: function(frm) {
		frm.clear_table("taxes");
        frm.refresh_field('taxes');
        frm.clear_table('purchase_taxes');
        frm.refresh_field('purchase_taxes');
        frm.call({
            method: 'item_tax_template',
            doc: frm.doc,
        })

    },
    rate: function(frm) {
		frm.clear_table("taxes");
        frm.refresh_field('taxes');
        frm.clear_table('purchase_taxes');
        frm.refresh_field('purchase_taxes');
        frm.call({
            method: 'call_two',
            doc: frm.doc,
        })

    },
    qty: function(frm) {
		frm.clear_table("taxes");
        frm.refresh_field('taxes');
        frm.clear_table('purchase_taxes');
        frm.refresh_field('purchase_taxes');
        frm.call({
            method: 'call_two',
            doc: frm.doc,
        })

    },
});

frappe.ui.form.on("Open Order Details", {
	qty:function(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	var total_qty = 0;
	var total_amount = 0;
	frm.doc.items.forEach(function(d) 
	{ 
		total_qty += d.qty;
		total_amount += d.amount;

	});
	frm.set_value("total_qty", total_qty);
	refresh_field("total_qty");
	frm.set_value("total_amount", total_amount);
	refresh_field("total_amount");
  },
  rate:function(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	var total_qty = 0;
	var total_amount = 0;
	frm.doc.items.forEach(function(d) 
	{ 
		total_qty += d.qty;
		total_amount += d.amount;

	});
	frm.set_value("total_qty", total_qty);
	refresh_field("total_qty");
	frm.set_value("total_amount", total_amount);
	refresh_field("total_amount");
  },
   items_remove:function(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	var total_qty = 0;
	var total_amount = 0;
	frm.doc.items.forEach(function(d) 
	{ 
	total_qty += d.qty;
	total_amount += d.amount; 

	});
	frm.set_value("total_qty", total_qty);
	refresh_field("total_qty");
	frm.set_value("total_amount", total_amount);
	refresh_field("total_amount");
   }
 });

frappe.ui.form.on('Open Order', {
refresh(frm){
         frm.trigger("make_sales_order")     
    },
    make_sales_order(frm){       
            if(frm.doc.docstatus == 1){
                frm.add_custom_button(__("Sales Order"),() => {
                    if (frm.doc.blanket_order_type == "Selling")
                        {
                            frappe.model.open_mapped_doc({
                            method:"quantbit_foundry_erp.quantbit_foundry_erp.doctype.open_order.open_order.make_sales_order",
                            frm:frm
                    })}
                    
                },__("Make")
                )
        frm.add_custom_button(__("Purchase Order"),() => {
            if (frm.doc.blanket_order_type == "Purchasing")
                {
                    frappe.model.open_mapped_doc({
                    method:"quantbit_foundry_erp.quantbit_foundry_erp.doctype.open_order.open_order.make_purchase_order",
                    frm:frm
            })}
    
    },__("Make"))
    }
}

});