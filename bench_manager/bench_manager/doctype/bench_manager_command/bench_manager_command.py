# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt


from subprocess import PIPE, Popen, check_output

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class BenchManagerCommand(Document):
	pass
