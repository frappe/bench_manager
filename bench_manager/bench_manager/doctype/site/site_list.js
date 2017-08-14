frappe.listview_settings['Site'] = {
	onload: function(me) {
		me.page.set_title(__("Sites"));
	},
	add_fields: ["site_name", "status"],
	get_indicator: function(doc) {
		if(doc.status) {
			return [__("existent"), "green", "status,=,existent"];
		} else {
			return [__("archived"), "darkgrey", "status,=,archived"];
		}
	}
}
