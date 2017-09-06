// Copyright (c) 2017, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bench Settings', {
	onload: function(frm) {
		let site_config_fields = ["background_workers", "shallow_clone", "admin_password",
			"auto_email_id", "auto_update", "frappe_user", "global_help_setup",
			"dropbox_access_key", "dropbox_secret_key", "gunicorn_workers", "github_username",
			"github_password", "mail_login", "mail_password", "mail_port", "mail_server",
			"use_tls", "rebase_on_pull", "redis_cache", "redis_queue", "redis_socketio",
			"restart_supervisor_on_update", "root_password", "serve_default_site",
			"socketio_port", "update_bench_on_update", "webserver_port", "developer_mode",
			"file_watcher_port"];
		site_config_fields.forEach(function(val){
			frm.toggle_display(val, frm.doc[val] != undefined);
		});
	},
	refresh: function(frm) {
		frm.add_custom_button(__("Update"), function(){
			let key = frappe.datetime.get_datetime_as_string();
			console_dialog(key);
			frappe.call({
				method: 'bench_manager.bench_manager.utils.console_command',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name,
					commands: "bench update",
					key: key
				},
				btn: this
			});
		});
		frm.add_custom_button(__('Sync'), () => {
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench_settings.bench_settings.sync_all'
			});
		});
		// frm.add_custom_button(__('Switch Branch'), function(){
		// 	frappe.call({
		// 		method: 'bench_manager.bench_manager.doctype.app.app.get_branches',
		// 		args: {
		// 			doctype: frm.doctype,
		// 			docname: 'frappe',
		// 			current_branch: frm.doc.frappe_git_branch
		// 		},
		// 		btn: this,
		// 		callback: function(r) {
		// 			var dialog = new frappe.ui.Dialog({
		// 				title: 'Select Branch',
		// 				fields: [
		// 					{'fieldname': 'switchable_branches', 'fieldtype': 'Select', options: r.message}
		// 				],
		// 			});
		// 			dialog.set_primary_action(__("Switch"), () => {
		// 				let key = frappe.datetime.get_datetime_as_string();
		// 				console_dialog(key);
		// 				frappe.call({
		// 					method: 'bench_manager.bench_manager.utils.console_command',
		// 					args: {
		// 						doctype: frm.doctype,
		// 						docname: 'frappe',
		// 						branch_name: cur_dialog.fields_dict.switchable_branches.value,
		// 						key: key,
		// 						bench_command: 'switch-to-branch',
		// 						cwd: '../apps/frappe'
		// 					},
		// 					callback: function(){
		// 						dialog.hide();
		// 					}
		// 				});
		// 			});
		// 			dialog.show();
		// 		}
		// 	});
		// });
	}
});