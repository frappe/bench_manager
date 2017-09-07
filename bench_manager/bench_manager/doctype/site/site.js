// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site', {
	onload: function(frm) {
		if (frm.doc.__islocal != 1){
			frm.save();
		}
		frappe.realtime.on("Bench-Manager:reload-page", () => {
			frm.reload_doc();
		});
	},
	validate: function(frm) {
		if (frm.doc.db_name == undefined) {
			let key = frappe.datetime.get_datetime_as_string();
			console_dialog(key);
			frm.doc.key = key;
		}
	},
	refresh: function(frm) {
		$('a.grey-link:contains("Delete")').hide();
		if (frm.doc.db_name == undefined) {
			$('div.form-inner-toolbar').hide();
		} else {
			$('div.form-inner-toolbar').show();
		}
		let single_function_buttons = {
			'Migrate': ' migrate',
			'Backup Site': ' backup --with-files'
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
						commands: "bench --site " + frm.doc.name + single_function_buttons[bench_command]
					},
					btn: this
				});
			});
		}
		frm.add_custom_button(__("Reinstall"), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.pass_exists',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function(r){
					var dialog = new frappe.ui.Dialog({
						title: "Are you sure?",
						fields: [
							{fieldname: 'admin_password', fieldtype: 'Password',
								label: 'Administrator Password', reqd: r['message']['condition'][0] != 'T',
								default: (r['message']['admin_password'] ? r['message']['admin_password'] :'admin'),
								depends_on: `eval:${String(r['message']['condition'][0] != 'T')}`}
						]
					});
					dialog.set_primary_action(__("Reinstall"), () => {
						let key = frappe.datetime.get_datetime_as_string();
						console_dialog(key);
						frappe.call({
							method: 'bench_manager.bench_manager.utils.console_command',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								key: key,
								commands: `bench --site ${frm.doc.name} reinstall --yes --admin-password ${dialog.fields_dict.admin_password.value}`
							},
							btn: this,
							callback: () => {
								dialog.hide();
							}
						});
					});
					dialog.show();
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
						let key = frappe.datetime.get_datetime_as_string();
						console_dialog(key);
						frappe.call({
							method: 'bench_manager.bench_manager.utils.console_command',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								key: key,
								commands: "bench --site "+ frm.doc.name + " install-app " + cur_dialog.fields_dict.installable_apps.value
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
								key: key,
								commands: `bench --site ${frm.doc.name} uninstall-app ${cur_dialog.fields_dict.removable_apps.value} --yes`
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
		frm.add_custom_button(__('Drop Site'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.pass_exists',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function(r){
					var dialog = new frappe.ui.Dialog({
						title: "Are you sure?",
						fields: [
							{fieldname: 'admin_password', fieldtype: 'Password',
								label: 'Administrator Password', reqd: r['message']['condition'][0] != 'T',
								default: (r['message']['admin_password'] ? r['message']['admin_password'] :'admin'),
								depends_on: `eval:${String(r['message']['condition'][0] != 'T')}`},
							{fieldname: 'mysql_password', fieldtype: 'Password',
								label: 'MySQL Password', reqd: r['message']['condition'][1] != 'T',
								default: r['message']['root_password'], depends_on: `eval:${String(r['message']['condition'][1] != 'T')}`}
						],
					});
					dialog.set_primary_action(__("Drop"), () => {
						let key = frappe.datetime.get_datetime_as_string();
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.verify_password',
							args: {
								site_name: frm.doc.name,
								mysql_password: dialog.fields_dict.mysql_password.value
							},
							callback: function(r){
								if (r.message == "console"){
									$('a.grey-link:contains("Delete")').click();
									$('button.btn.btn-primary.btn-sm:contains("Yes")').click();
									setTimeout( () => {
										console_dialog(key);
										frappe.call({
											method: 'bench_manager.bench_manager.utils.console_command',
											args: {
												doctype: frm.doctype,
												docname: frm.doc.name,
												commands: `bench drop-site ${frm.doc.name} --root-password ${dialog.fields_dict.mysql_password.value}`,
												key: key
											}
										});
									}, 1000);
									dialog.hide();
								} 
							}
						});
					});
					dialog.show();
				}
			});
		});
	}
});