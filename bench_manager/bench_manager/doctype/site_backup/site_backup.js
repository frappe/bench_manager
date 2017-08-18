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
					var d = new frappe.ui.Dialog({
						fields: [
							{fieldname: 'on_a_new_site', fieldtype: 'Check', label: __("On a new site"),
								onchange: () => {
									let checked = d.get_value('on_a_new_site');
									if (checked) {
										$('div[data-fieldname="existing_sites"]').hide();
										$('div[data-fieldname="new_site_name"]').show();
									} else {
										$('div[data-fieldname="existing_sites"]').show();
										$('div[data-fieldname="new_site_name"]').hide();
									}
								}
							},
							{fieldname: 'existing_sites', fieldtype: 'Select', options: r.message, label:__("Existing Sites")},
							{fieldname: 'new_site_name', fieldtype: 'Data', label:__("New Site Name")}
						],
					});
					d.set_primary_action(__("Restore"), () => {
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site_backup.site_backup.restore_backup',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								on_a_new_site: cur_dialog.fields_dict.on_a_new_site.last_value,
								existing_site: cur_dialog.fields_dict.existing_sites.get_input_value(),
								new_site_name: cur_dialog.fields_dict.new_site_name.get_input_value()
							},
							callback: function(){
								d.hide();
								frm.save();
								frappe.msgprint('Done');
							}
						});

					});
					d.show();
					$('div[data-fieldname="new_site_name"]').hide();
				}
			});
		});
	}
});
