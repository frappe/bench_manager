// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site', {
	refresh: function(frm) {
		frm.add_custom_button(__('Install app'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.get_installable_apps',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function(r) {
					var d = new frappe.ui.Dialog({
					    fields: [
					        {'fieldname': 'installable_apps', 'fieldtype': 'Select', options: r.message}
					    ],
					});
					d.set_primary_action(__("Install"), () => {
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.install_app',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: $('.input-with-feedback.form-control:visible').val()
							},
							callback: function(){
								d.hide();
								frm.save();
							}
						});

					});
					d.show();
				}
			});
		});
		frm.add_custom_button(__('Uninstall app'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.get_removable_apps',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function(r) {
					var d = new frappe.ui.Dialog({
					    fields: [
					        {'fieldname': 'removable_apps', 'fieldtype': 'Select', options: r.message}
					    ],
					});
					d.set_primary_action(__("Remove"), () => {
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.remove_app',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: $('.input-with-feedback.form-control:visible').val()
							},
							callback: function(){
								d.hide();
								frm.save();
							}

						});

					});
					d.show();
				}
			});
		});
	}
});