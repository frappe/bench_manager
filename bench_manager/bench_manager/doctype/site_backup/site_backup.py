# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SiteBackup(Document):
	def autoname(self):
		if self.site_name == None:
			return
		self.name = self.site_name +' '+ self.date +' '+ self.time

	def validate(self):
		if self.get("__islocal"):
			if self.bypass_flag == 0:
				frappe.throw("If you want to create a backup, then goto Sites")

@frappe.whitelist()
def get_restore_options(doctype, docname):
	return [x['name'] for x in frappe.get_all('Site')]

@frappe.whitelist()
def restore_backup(doctype, docname, on_a_new_site, existing_sites, new_site_name):
	if on_a_new_site:
		pass
	