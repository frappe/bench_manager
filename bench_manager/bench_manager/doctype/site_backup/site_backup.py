# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import check_output

class SiteBackup(Document):
	def autoname(self):
		if self.site_name == None:
			return
		self.name = self.site_name +' '+ self.date +' '+ self.time

	def validate(self):
		if self.get("__islocal"):
			if self.developer_flag == 0:
				frappe.throw("If you want to create a backup, then goto Sites")
			self.developer_flag = 0

	def on_trash(self):
		if self.developer_flag == 0:
			check_output('rm ' + self.file_path + '_database.sql*',
				shell=True, cwd='..')
			if self.public_file_backup:
				check_output('rm ' + self.file_path + '_files.tar',
					shell=True, cwd='..')
			if self.private_file_backup:
				check_output('rm ' + self.file_path + '_private_files.tar',
					shell=True, cwd='..')
			frappe.msgprint('Backup deleted !')
		else:
			frappe.msgprint('Deleting the entry but not the Backup')

@frappe.whitelist()
def get_restore_options(doctype, docname):
	return [x['name'] for x in frappe.get_all('Site')]

@frappe.whitelist()
def restore_backup(doctype, docname, on_a_new_site, existing_site, new_site_name):
	if on_a_new_site:
		try:
			doc = frappe.get_doc({'doctype': 'Site', 'site_name': new_site_name})
			x = doc.insert()
			backup = frapp.get_doc('Site Backup', docname)
			str_to_exec = 'bench --site ' + existing_site + ' --force restore ' + backup.file_path + '_database.sql*'
			if backup.public_file_backup:
				str_to_exec += ' --with-public-files ../' + backup.file_path + '_files.tar'
			if backup.private_file_backup:
				str_to_exec += ' --with-private-files ../' + backup.file_path + '_private_files.tar'
			terminal = check_output(str_to_exec, shell=True, cwd='..')
		except:
			frappe.throw('Something went wrong. Please contact tech support!')
	else:
		backup = frappe.get_doc('Site Backup', docname)
		str_to_exec = 'bench --site ' + existing_site + ' --force restore ' + backup.file_path + '_database.sql*'
		if backup.public_file_backup:
			str_to_exec += ' --with-public-files ../' + backup.file_path + '_files.tar'
		if backup.private_file_backup:
			str_to_exec += ' --with-private-files ../' + backup.file_path + '_private_files.tar'
		terminal = check_output(str_to_exec, shell=True, cwd='..')
