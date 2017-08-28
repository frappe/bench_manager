frappe.listview_settings['Site'] = {
	formatters: {
		app_list: function(val) {
			return val.split('\n').join(', ');
		}		
	}
};