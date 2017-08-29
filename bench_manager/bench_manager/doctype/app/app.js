// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('App', {
	// validate: function(frm) {
	// 	if (frm.doc.version == undefined) {
	// 		let key = frappe.datetime.get_datetime_as_string();
	// 		console_dialog(key);
	// 		frm.doc.key = key;
	// 	}
	// },
	refresh: function(frm) {
		let app_fields = ["app_title", "version", "app_description", "app_publisher", "app_email",
			"app_icon", "app_color", "app_license"];
		app_fields.forEach(function(app_field) {
			frm.set_df_property(app_field, "read_only", frm.doc.__islocal ? 0 : 1);
		});
		if (frm.doc.is_git_repo == false) {
			frm.add_custom_button(__("Git Init"), function(){
				let key = frappe.datetime.get_datetime_as_string();
				console_dialog(key);
				frm.doc.is_git_repo = true;
				frappe.call({
					method: 'bench_manager.bench_manager.utils.console_command',
					args: {
						doctype: frm.doctype,
						docname: frm.doc.name,
						key: key,
						bench_command: 'git-init',
						cwd: '../apps/'+frm.doc.name
					},
					btn: this,
					callback: function(r) {
						setTimeout(function() { frm.save(); }, 5000);
					}
				});
			});
		} else {
			frm.add_custom_button(__('Switch Branch'), function(){
				frappe.call({
					method: 'bench_manager.bench_manager.doctype.app.app.get_branches',
					args: {
						doctype: frm.doctype,
						docname: frm.doc.name,
						current_branch: frm.doc.current_git_branch
					},
					btn: this,
					callback: function(r) {
						var dialog = new frappe.ui.Dialog({
							title: 'Select Branch',
							fields: [
								{'fieldname': 'switchable_branches', 'fieldtype': 'Select', options: r.message}
							],
						});
						dialog.set_primary_action(__("Switch"), () => {
							let key = frappe.datetime.get_datetime_as_string();
							console_dialog(key);
							frappe.call({
								method: 'bench_manager.bench_manager.utils.console_command',
								args: {
									doctype: frm.doctype,
									docname: frm.doc.name,
									branch_name: cur_dialog.fields_dict.switchable_branches.value,
									key: key,
									bench_command: 'switch-to-branch',
									cwd: '../apps/'+frm.doc.name
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
			frm.add_custom_button(__('New Branch'), function(){
				frappe.call({
					method: 'bench_manager.bench_manager.doctype.app.app.new_git_branch',
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
		}
	}
});