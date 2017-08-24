// Copyright (c) 2017, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('App', {
	validate: function(frm) {
		if (frm.doc.version == undefined) {
			let key = frappe.datetime.get_datetime_as_string();
			console_dialog(key);
			frm.doc.key = key;
		}
	},
	refresh: function(frm) {
		let app_fields = ["app_title", "version", "app_description", "app_publisher", "app_email",
			"app_icon", "app_color", "app_license"];
		app_fields.forEach(function(app_field) {
			frm.set_df_property(app_field, "read_only", frm.doc.__islocal ? 0 : 1);
		});
	}
});