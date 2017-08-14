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
			})
		});
		frm.add_custom_button(__('Sync Sites'), () => {
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench.bench.sync_sites',
				args: {
					doctype: 'Site'
				}
			})
		});
		frm.add_custom_button(__('Sync Apps'), () => {
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.bench.bench.sync_apps',
				args: {
					doctype: 'App'
				}
			})
		});
	}
});

frappe.realtime.on('terminal_output', function(output) {
	// if (output==='\r') {
	// 	// clear current line, means we are showing some kind of progress indicator
	// 	frappe._in_progress = true;
	// 	if(frappe._output_target.innerHTML != frappe._output) {
	// 		// progress updated... redraw
	// 		frappe._output_target.innerHTML = frappe._output;
	// 	}
	// 	frappe._output = frappe._output.split('\n').slice(0, -1).join('\n') + '\n';
	// 	return;
	// } else {
	// 	frappe._output += output;
	// }

	// if (output==='\n') {
	// 	frappe._in_progress = false;
	// }

	// if (frappe._in_progress) {
	// 	return;
	// }

	// if (!frappe._last_update) {
	// 	frappe._last_update = setTimeout(() => {
	// 		frappe._last_update = null;
	// 		if(!frappe.in_progress) {
	// 			frappe._output_target.innerHTML = frappe._output;
	// 		}
	// 	}, 200);
	// }
	frappe._output_target.innerHTML += output;
});