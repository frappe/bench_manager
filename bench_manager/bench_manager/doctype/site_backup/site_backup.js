// Copyright (c) 2017, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Backup', {
	refresh: function(frm) {
		frm.add_custom_button(__('Restore'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site_backup.site_backup.get_restore_options',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function(r) {
					var dialog_data = new frappe.ui.Dialog({
						title: 'Restore Options',
						fields: [
							{fieldname: 'on_a_new_site', fieldtype: 'Check', label: __("On a new site"),
								onchange: () => {
									let checked = dialog_data.get_value('on_a_new_site');
									if (checked) {
										$('div[data-fieldname="existing_sites"]').hide();
										$('div[data-fieldname="new_site_name"]').show();
									} else {
										$('div[data-fieldname="existing_sites"]').show();
										$('div[data-fieldname="new_site_name"]').hide();
									}
								}
							},
							{fieldname: 'existing_sites', fieldtype: 'Select', options: r.message,
								label:__("Existing Sites")},
							{fieldname: 'new_site_name', fieldtype: 'Data', label:__("New Site Name")}
						],
					});
					dialog_data.set_primary_action(__("Verify"), () => {
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.pass_exists',
							args: {
								doctype: frm.doctype,
								docname: dialog_data.fields_dict.on_a_new_site.last_value != 1 ? '' : dialog_data.fields_dict.existing_sites.get_input_value()
							},
							btn: this,
							callback: function(r){
								var verification_dialog = new frappe.ui.Dialog({
									title: 'Are you sure?',
									fields: [
										{fieldname: 'admin_password', fieldtype: 'Password',
											label: 'Administrator Password', reqd: r['message']['condition'][0] != 'T',
											default: (r['message']['admin_password'] ? r['message']['admin_password'] :'admin'),
											depends_on: `eval:${String(r['message']['condition'][0] != 'T')}`},
										{fieldname: 'mysql_password', fieldtype: 'Password',
											label: 'MySQL Password', reqd: r['message']['condition'][1] != 'T',
											default: r['message']['root_password'], depends_on: `eval:${String(r['message']['condition'][1] != 'T')}`}
									]
								});
								verification_dialog.set_primary_action(__("Restore"), () => {
									frappe.call({
										method: 'bench_manager.bench_manager.doctype.site.site.verify_password',
										args: {
											site_name: dialog_data.fields_dict.on_a_new_site.last_value != 1 ? '' : dialog_data.fields_dict.existing_sites.get_input_value(),
											mysql_password: verification_dialog.fields_dict.mysql_password.value
										},
										callback: function(r){
											if (r.message == "console"){
												let key = frappe.datetime.get_datetime_as_string();
												console_dialog(key);
												frappe.call({
													method: 'bench_manager.bench_manager.doctype.site_backup.site_backup.restore_backup',
													args: {
														doctype: frm.doctype,
														docname: frm.doc.name,
														on_a_new_site: dialog_data.fields_dict.on_a_new_site.last_value,
														existing_site: dialog_data.fields_dict.existing_sites.get_input_value(),
														new_site_name: dialog_data.fields_dict.new_site_name.get_input_value(),
														mysql_password: verification_dialog.fields_dict.mysql_password.value,
														admin_password: verification_dialog.fields_dict.admin_password.value,
														key: key
													},
													callback: function(){
														dialog_data.hide();
														verification_dialog.hide();
													}
												});
											} 
										}
									});
								});
								verification_dialog.show();
							}
						});
					});
					dialog_data.show();
					$('div[data-fieldname="new_site_name"]').hide();
				}
			});
		});
	}
});