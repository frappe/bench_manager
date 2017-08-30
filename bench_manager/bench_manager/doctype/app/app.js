// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('App', {
	onload: function(frm) {
		if (!cur_frm.doc.__islocal){
			frm.save();
		}
	},
	refresh: function(frm) {
		if (frm.doc.version == undefined) {
			$('div.form-inner-toolbar').hide();
		} else {
			$('div.form-inner-toolbar').show();
		}
		let app_fields = ["app_title", "version", "app_description", "app_publisher", "app_email",
			"app_icon", "app_color", "app_license"];
		app_fields.forEach(function(app_field) {
			frm.set_df_property(app_field, "read_only", frm.doc.__islocal ? 0 : 1);
		});
		if (frm.doc.is_git_repo != true) {
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
				var dialog = new frappe.ui.Dialog({
					title: 'Create New Branch',
					fields: [
						{'fieldname': 'new_branch_name', 'fieldtype': 'Data'}
					],
				});
				dialog.set_primary_action(__("Create"), () => {
					let key = frappe.datetime.get_datetime_as_string();
					console_dialog(key);
					frappe.call({
						method: 'bench_manager.bench_manager.utils.console_command',
						args: {
							doctype: frm.doctype,
							docname: frm.doc.name,
							branch_name: cur_dialog.fields_dict.new_branch_name.value,
							key: key,
							bench_command: 'create-branch',
							cwd: '../apps/'+frm.doc.name
						},
						callback: function(){
							dialog.hide();
						}
					});
				});
				dialog.show();
			});
			frm.add_custom_button(__('Delete Branch'), function(){
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
								{'fieldname': 'delete_branch_name', 'fieldtype': 'Select', options: r.message}
							],
						});
						dialog.set_primary_action(__("Delete"), () => {
							let key = frappe.datetime.get_datetime_as_string();
							console_dialog(key);
							frappe.call({
								method: 'bench_manager.bench_manager.utils.console_command',
								args: {
									doctype: frm.doctype,
									docname: frm.doc.name,
									branch_name: cur_dialog.fields_dict.delete_branch_name.value,
									key: key,
									bench_command: 'delete-branch',
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
			frm.add_custom_button(__('Fetch'), function(){
				let key = frappe.datetime.get_datetime_as_string();
				console_dialog(key);
				frappe.call({
					method: 'bench_manager.bench_manager.utils.console_command',
					args: {
						doctype: frm.doctype,
						docname: frm.doc.name,
						key: key,
						bench_command: 'git-fetch',
						cwd: '../apps/'+frm.doc.name
					}
				});
			});
		}
	}
});