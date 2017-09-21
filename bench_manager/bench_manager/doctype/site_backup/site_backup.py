# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import check_output
from bench_manager.bench_manager.utils import verify_whitelisted_call

class SiteBackup(Document):
	def autoname(self):
		if self.site_name == None:
			return
		self.name = self.date +' '+ self.time +' '+ self.site_name +' '+ self.stored_location

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
		else:
			pass
			# frappe.msgprint('Deleting the entry but not the Backup')

	# def convert_date(self):
	# 	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
	# 		'August', 'September', 'October', 'November', 'December']
	# 	date_str = self.date.split(' ')
	# 	date = date_str[2]
	# 	date += "-"+str(months.index(date_str[1])).zfill(2)
	# 	date += "-"+date_str[0]
	# 	return date

@frappe.whitelist()
def get_restore_options(doctype, docname):
	verify_whitelisted_call()
	return [x['name'] for x in frappe.get_all('Site')]

@frappe.whitelist()
def restore_backup(doctype, docname, on_a_new_site, existing_site, new_site_name, mysql_password, admin_password, key):
	verify_whitelisted_call()
	backup = frappe.get_doc('Site Backup', docname)
	commands = []
	password_suffix = "--admin-password {admin_password} --mariadb-root-password {mysql_password}".format(mysql_password=mysql_password, admin_password=admin_password)
	site_name = existing_site
	if on_a_new_site == '1':
		site_name = new_site_name
		commands.append("bench new-site {site_name} {password_suffix}".format(site_name=site_name,
			password_suffix=password_suffix))
	command = "bench --site {site_name} --force restore {backup_file_path}_database.sql".format(site_name=site_name, backup_file_path=backup.file_path)
	if not os.path.isfile("{backup_file_path}_database.sql".format(backup_file_path=backup.file_path)):
		command += ".gz"
	if backup.public_file_backup:
		command += " --with-public-files ../{backup_file_path}_files.tar".format(backup_file_path=backup.file_path)
	if backup.private_file_backup:
		command += " --with-private-files ../{backup_file_path}_private_files.tar".format(backup_file_path=backup.file_path)
	command += " {password_suffix}".format(password_suffix=password_suffix)
	commands.append(command)
	frappe.enqueue('bench_manager.bench_manager.utils.run_command',
		commands=commands,
		doctype=doctype,
		key=key,
		docname=docname
	)