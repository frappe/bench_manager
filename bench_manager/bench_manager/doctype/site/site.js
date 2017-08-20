// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site', {
	refresh: function(frm) {
		frm.add_custom_button(__('Migrate'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.migrate',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function() {
					frappe.msgprint('Done');
				}
			});
		});
		frm.add_custom_button(__('Backup Site'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.backup_site',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function() {
					frappe.msgprint('Done');
				}
			});
		});
		frm.add_custom_button(__('Install App'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.get_installable_apps',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function(r) {
					var dialog = new frappe.ui.Dialog({
						title: 'Select App',
						fields: [
							{'fieldname': 'installable_apps', 'fieldtype': 'Select', options: r.message}
						],
					});
					dialog.set_primary_action(__("Install"), () => {
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.install_app',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: cur_dialog.fields_dict.installable_apps.value
							},
							callback: function(){
								dialog.hide();
								frm.save();
							}
						});

					});
					dialog.show();
				}
			});
		});
		frm.add_custom_button(__('Uninstall App'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.get_removable_apps',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function(r) {
					var dialog = new frappe.ui.Dialog({
						title: 'Select App',
						fields: [
							{'fieldname': 'removable_apps', 'fieldtype': 'Select', options: r.message},
						],
					});
					dialog.set_primary_action(__("Remove"), () => {
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.remove_app',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: cur_dialog.fields_dict.removable_apps.value
							},
							callback: function(){
								dialog.hide();
								frm.save();
							}

						});

					});
					dialog.show();
				}
			});
		});
	}
});