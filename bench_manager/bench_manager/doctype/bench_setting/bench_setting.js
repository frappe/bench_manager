// Copyright (c) 2017, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bench Setting', {
	onload: function(frm) {
		frappe._output_target = $('<pre class="console"><code></code></pre>')
			.appendTo(frm.get_field('run_command_output').wrapper)
			.find('code')
			.get(0);
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
					bench_command: 'update',
					key: key
				},
				btn: this
			});
		});
		frm.add_custom_button(__('Sync Backups'), () => {
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench_setting.bench_setting.sync_backups'
			});
		});
		frm.add_custom_button(__('Sync Sites'), () => {
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench_setting.bench_setting.sync_sites'
			});
		});
		frm.add_custom_button(__('Sync Apps'), () => {
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench_setting.bench_setting.sync_apps'
			});
		});
	}
});