// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bench', {
	onload: function(frm) {
		frappe._output_target = $('<pre class="console"><code></code></pre>')
			.appendTo(frm.get_field('run_command_output').wrapper)
			.find('code')
			.get(0);
	},
	refresh: function(frm) {
		frm.add_custom_button(__('Update'), () => {
			frappe._output = '';
			frappe._in_progress = false;
			frappe._output_target.innerHTML = '';
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench.bench.bench_update',
				args: {
					command: 'bench update'
				}
			});
		});
		frm.add_custom_button(__('Sync Backups'), () => {
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench.bench.sync_backups'
			});
		});
		frm.add_custom_button(__('Sync Sites'), () => {
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench.bench.sync_sites'
			});
		});
		frm.add_custom_button(__('Sync Apps'), () => {
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench.bench.sync_apps'
			});
		});
	}
});

frappe.realtime.on('terminal_output', function(output) {
	frappe._output_target.innerHTML += output;
});