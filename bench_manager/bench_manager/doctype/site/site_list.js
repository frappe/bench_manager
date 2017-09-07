frappe.listview_settings['Site'] = {
	formatters: {
		app_list: function(val) {
			return val.split('\n').join(', ');
		}		
	},
	onload: function(list) {
		frappe.realtime.on("Bench-Manager:drop-site", (data) => {
			let key = frappe.datetime.get_datetime_as_string();
			console_dialog(key);
			frappe.call({
				method: 'bench_manager.bench_manager.utils.console_command',
				args: {
					doctype: list.doctype,
					docname: data.site_name,
					key: key,
					commands: "bench drop-site " + data.site_name
				},
				btn: this
			});
		});
	},
	refresh: () => {
		setTimeout( () => {
			$("input.list-select-all.hidden-xs").hide()
		}, 500);
		setTimeout( () => {
			$("input.list-row-checkbox.hidden-xs").hide()
		}, 500);
	}
};