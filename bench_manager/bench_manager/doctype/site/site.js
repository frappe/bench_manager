// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site', {
	validate: function(frm) {
		if (frm.doc.db_name == undefined) {
			let key = frappe.datetime.get_datetime_as_string();
			console_dialog(key);
			frm.doc.key = key;
		}
	},
	onload: function(frm) {
		let site_config_fields = ["maintenance_mode", "pause_scheduler", "db_name", "db_password",
			"developer_mode", "emails", "expiry", "space", "backup_size", "database_size", "files_size", "total"];
		site_config_fields.forEach(function(val){
			frm.toggle_display(val, frm.doc[val] != undefined);
		});
	},
	refresh: function(frm) {
		$("a.grey-link:contains('Delete')").click(function() {
			$("button.btn:contains('No')").click()
			let key = frappe.datetime.get_datetime_as_string();
			console_dialog(key);
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.ui_on_trash',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name,
					key: key
				},
				btn: this
			});
			
		});
		if (frm.doc.db_name == undefined) {
			$('div.form-inner-toolbar').hide();
		} else {
			$('div.form-inner-toolbar').show();
		}
		let single_function_buttons = {
			'Migrate': 'migrate',
			'Reinstall': 'reinstall',
			'Backup Site': 'backup_site'
		};
		for (let bench_command in single_function_buttons){
			frm.add_custom_button(__(bench_command), function(){
				let key = frappe.datetime.get_datetime_as_string();
				console_dialog(key);
				frappe.call({
					method: 'bench_manager.bench_manager.utils.console_command',
					args: {
						doctype: frm.doctype,
						docname: frm.doc.name,
						key: key,
						bench_command: single_function_buttons[bench_command]
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
							method: 'bench_manager.bench_manager.utils.console_command',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: cur_dialog.fields_dict.installable_apps.value,
								key: key,
								bench_command: 'install_app'								
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
							method: 'bench_manager.bench_manager.utils.console_command',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: cur_dialog.fields_dict.removable_apps.value,
								key: key,
								bench_command: 'remove_app'
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