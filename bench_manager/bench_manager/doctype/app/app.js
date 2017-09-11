// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('App', {
	onload: function(frm) {
		if (frm.doc.__islocal != 1){
			frm.save();
		}
		frappe.realtime.on("Bench-Manager:reload-page", () => {
			frm.reload_doc();
		});
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
						commands: "git init\rgit add .\rgit commit -m 'Initial Commit'",
						cwd: '../apps/'+frm.doc.name
					},
					btn: this,
					callback: function() {
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
									key: key,
									commands: "git checkout " + cur_dialog.fields_dict.switchable_branches.value,
									cwd: '../apps/'+frm.doc.name
								},
								callback: function(){
									frappe.publish_realtime("Bench-Manager:reload-page");
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
							key: key,
							commands: "git branch "+cur_dialog.fields_dict.new_branch_name.value,
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
									key: key,
									commands: "git branch -D "+cur_dialog.fields_dict.delete_branch_name.value,
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
						commands: "git fetch --all",
						cwd: '../apps/'+frm.doc.name
					}
				});
			});
		}
	}
});
