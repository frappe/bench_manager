# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Bench Manager",
			"color": "black",
			"icon": "fa fa-gamepad",
			"type": "module",
			"label": _("Bench Manager"),
			"link": "Form/Bench Settings"
		}
	]
