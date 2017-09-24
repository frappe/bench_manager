// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site', {
	onload: function(frm) {
		if (frm.doc.__islocal != 1) {
			frm.save();
			frm.call("update_app_alias");
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
		if (frm.doc.db_name == undefined) $('div.form-inner-toolbar').hide();
		else $('div.form-inner-toolbar').show();
		frm.add_custom_button(__('Create Alias'), function(){
			var dialog = new frappe.ui.Dialog({
				title: 'Alias Name',
				fields: [
					{fieldname: 'alias', fieldtype: 'Data', reqd:true}
				]
			});
			dialog.set_primary_action(__("Create Alias"), () => {
				let key = frappe.datetime.get_datetime_as_string();
				console_dialog(key);
				frm.call("create_alias", {
					key: key,
					alias: dialog.fields_dict.alias.value
				}, () => {
					dialog.hide();
				});
			});
			dialog.show();
		});
		frm.add_custom_button(__('Delete Alias'), function(){
			let alias_list = frm.doc.site_alias.split('\n');
			alias_list.pop();
			var dialog = new frappe.ui.Dialog({
				title: 'Alias Name',
				fields: [
					{fieldname: 'alias', fieldtype: 'Select', reqd:true, options:alias_list}
				]
			});
			dialog.set_primary_action(__("Delete Alias"), () => {
				let key = frappe.datetime.get_datetime_as_string();
				console_dialog(key);
				frm.call("console_command", {
					key: key,
					caller: "delete-alias",
					alias: dialog.fields_dict.alias.value
				}, () => {
					dialog.hide();
				});
			});
			dialog.show();
		});
		frm.add_custom_button(__("Migrate"), function() {
			let key = frappe.datetime.get_datetime_as_string();
			console_dialog(key);
			frm.call("console_command", {
				key: key,
				caller: "migrate",
			});
		});
		frm.add_custom_button(__("Backup"), function() {
			let key = frappe.datetime.get_datetime_as_string();
			console_dialog(key);
			frm.call("console_command", {
				key: key,
				caller: "backup",
			});
		});
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
						frm.call("console_command", {
							key: key,
							caller: "reinstall",
							admin_password: dialog.fields_dict.admin_password.value
						}, () => {
							dialog.hide();
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
						frm.call("console_command", {
							key: key,
							caller: "install_app",
							app_name: dialog.fields_dict.installable_apps.value
						}, () => {
							dialog.hide();
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
						]
					});
					dialog.set_primary_action(__("Remove"), () => {
						let key = frappe.datetime.get_datetime_as_string();
						console_dialog(key);
						frm.call("console_command", {
							key: key,
							caller: "uninstall_app",
							app_name: dialog.fields_dict.removable_apps.value
						}, () => {
							dialog.hide();
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
									frappe.run_serially([
										() => console_dialog(key),
										() => frm.call("console_command", {
											key: key,
											caller: "drop_site",
											mysql_password: dialog.fields_dict.mysql_password.value
										}, () => {
											frappe.run_serially([
												$('a.grey-link:contains("Delete")').click(),
												$('button.btn.btn-primary.btn-sm:contains("Yes")').click()
											]);
										}),
										() => dialog.hide()
									]);
									
									
								}
							}
						});
					});
					dialog.show();
				}
			});
		});
		frm.add_custom_button(__('View site'), () => {
			frappe.db.get_value('Bench Settings', 'Bench Settings', 'webserver_port',
				(r) => {
					window.open(`http://${frm.doc.name}:${r.webserver_port}`, '_blank');
				}
			);
		});
	}
});