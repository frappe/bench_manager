// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

var console_dialog = (key) => {
	var dialog = new frappe.ui.Dialog({
		title: 'Console',
		fields: [
			{fieldname: 'console', fieldtype: 'HTML'},
		]
	});
	frappe._output_target = $('<pre class="console"><code></code></pre>')
		.appendTo(dialog.get_field('console').wrapper)
		.find('code')
		.get(0);
	frappe._output = '';
	frappe._in_progress = false;
	frappe._output_target.innerHTML = '';
	dialog.show();
	dialog.$wrapper.find('.modal-dialog').css('width', '800px');

	frappe.realtime.on(key, function(output) {
		if (output==='\r') {
			// clear current line, means we are showing some kind of progress indicator
			frappe._in_progress = true;
			if(frappe._output_target.innerHTML != frappe._output) {
				// progress updated... redraw
				frappe._output_target.innerHTML = frappe._output;
			}
			frappe._output = frappe._output.split('\n').slice(0, -1).join('\n') + '\n';
			return;
		} else {
			frappe._output += output;
		}

		if (output==='\n') {
			frappe._in_progress = false;
		}

		if (frappe._in_progress) {
			return;
		}

		if (!frappe._last_update) {
			frappe._last_update = setTimeout(() => {
				frappe._last_update = null;
				if(!frappe.in_progress) {
					frappe._output_target.innerHTML = frappe._output;
				}
			}, 200);
		}
	});
};