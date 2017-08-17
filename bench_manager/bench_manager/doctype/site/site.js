// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site', {
	refresh: function(frm) {
		frm.add_custom_button(__('Backup Site'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.backup_site',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function() {
					frappe.msgprint('Done');
				}
			});
		});
		frm.add_custom_button(__('Restore Backup'), function(){
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.restore_options',
				args: {
					doctype: frm.doctype,
					docname: frm.doc.name
				},
				btn: this,
				callback: function(r) {
					let backups = [];
					r.message.forEach(function(backup){
						backups.push(backup.site_name + ' * ' + backup.date + ' * ' + backup.time + 'hrs * ' +
							'('+backup.location+') * \'' + backup.hash + '\'');
					});
					var d = new frappe.ui.Dialog({
						fields: [
							{'fieldname': 'backup_options', 'fieldtype': 'Select', options: backups},
							{'fieldname': 'with_public_files', 'fieldtype': 'Check', label: __("With public files (if present)")},
							{'fieldname': 'with_private_files', 'fieldtype': 'Check', label: __("With private files (if present)")}
						],
					});
					d.set_primary_action(__("Restore"), () => {
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.restore_backup',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								backup_name: cur_dialog.fields_dict.backup_options.value,
								with_public_files: cur_dialog.fields_dict.with_public_files.input.checked,
								with_private_files: cur_dialog.fields_dict.with_private_files.input.checked
							},
							callback: function(){
								d.hide();
								frm.save();
								frappe.msgprint('Done');
							}
						});

					});
					d.show();
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
					var d = new frappe.ui.Dialog({
						fields: [
							{'fieldname': 'installable_apps', 'fieldtype': 'Select', options: r.message}
						],
					});
					d.set_primary_action(__("Install"), () => {
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.install_app',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: $('.input-with-feedback.form-control:visible').val()
							},
							callback: function(){
								d.hide();
								frm.save();
							}
						});

					});
					d.show();
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
					var d = new frappe.ui.Dialog({
						fields: [
							{'fieldname': 'removable_apps', 'fieldtype': 'Select', options: r.message},
						],
					});
					d.set_primary_action(__("Remove"), () => {
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.remove_app',
							args: {
								doctype: frm.doctype,
								docname: frm.doc.name,
								app_name: $('.input-with-feedback.form-control:visible').val()
							},
							callback: function(){
								d.hide();
								frm.save();
							}

						});

					});
					d.show();
				}
			});
		});
	}
});