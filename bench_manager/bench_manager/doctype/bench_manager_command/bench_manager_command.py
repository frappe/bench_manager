# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from subprocess import check_output, Popen, PIPE

class BenchManagerCommand(Document):
	pass