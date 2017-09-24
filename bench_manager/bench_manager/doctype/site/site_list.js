frappe.listview_settings['Site'] = {
	formatters: {
		app_list: function(val) {
			return val.split('\n').join(', ');
		},
		site_alias: function(val) {
			return val.split('\n').join(', ');
		}	
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