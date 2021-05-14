from frappe import _


def get_data():
	bench_setup = {
		"label": _("Bench Setup"),
		"icon": "octicon octicon-briefcase",
		"items": [
			{
				"name": "App",
				"type": "doctype",
				"label": _("App"),
				"description": _("Frappe Apps"),
			},
			{
				"name": "Site",
				"type": "doctype",
				"label": _("Site"),
				"description": _("Bench Sites"),
			},
		],
	}

	bench_management = {
		"label": _("Bench Management"),
		"type": "module",
		"items": [
			{
				"name": "Site Backup",
				"type": "doctype",
				"label": _("Site Backup"),
				"description": _("Site Backup"),
			},
			{
				"name": "Bench Manager Command",
				"type": "doctype",
				"label": _("Bench Manager Command"),
				"description": _("Bench Manager Command"),
			},
			{
				"name": "Bench Settings",
				"type": "doctype",
				"label": _("Bench Settings"),
				"description": _("Bench Settings"),
			},
		],
	}

	return [bench_setup, bench_management]
