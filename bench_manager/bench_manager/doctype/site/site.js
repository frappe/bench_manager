// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site', {
	refresh: function(frm) {
		let single_function_buttons = {
			'Migrate': 'bench_manager.bench_manager.doctype.site.site.migrate',
			'Reinstall': 'bench_manager.bench_manager.doctype.site.site.reinstall',
			'Backup Site': 'bench_manager.bench_manager.doctype.site.site.backup_site'
		};
		for (let button_name in single_function_buttons){
			frm.add_custom_button(__(button_name), function(){
				let key = frappe.datetime.get_datetime_as_string();
				console_dialog(key);
				frappe.call({
					method: single_function_buttons[button_name],
					args: {
						doctype: frm.doctype,
						docname: frm.doc.name,
						key: key
					},
					btn: this
				});
			});
		}
		// let multi_function_buttons = {
		// 	'Install App': {
		// 		method_one: 'bench_manager.bench_manager.doctype.site.site.get_installable_apps',
		// 		method_two: 'bench_manager.bench_manager.doctype.site.site.install_app',
		// 		fields: {'fieldname': 'installable_apps', 'fieldtype': 'Select', options: r.message},
		// 		button_name: 'Install',
		// 		app_name: cur_dialog.fields_dict.installable_apps.value
		// 	},
		// 	'Uninstall App': {
		// 		method_one: 'bench_manager.bench_manager.doctype.site.site.get_removable_apps',
		// 		method_two: 'bench_manager.bench_manager.doctype.site.site.remove_app',
		// 		fields: {'fieldname': 'removable_apps', 'fieldtype': 'Select', options: r.message},
		// 		button_name: 'Remove',
		// 		app_name: cur_dialog.fields_dict.removable_apps.value
		// 	},
		// };
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
						let key = frappe.datetime.get_datetime_as_string();
						console_dialog(key);
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.install_app',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: cur_dialog.fields_dict.installable_apps.value,
								key: key
							},
							callback: function(){
								dialog.hide();
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
						let key = frappe.datetime.get_datetime_as_string();
						console_dialog(key);
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.remove_app',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: cur_dialog.fields_dict.removable_apps.value,
								key: key
							},
							callback: function(){
								dialog.hide();
							}
						});
					});
					dialog.show();
				}
			});
		});
	}
});