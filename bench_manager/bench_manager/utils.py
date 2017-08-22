# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

@frappe.whitelist()
def console_command(doctype='', docname='', key='', bench_command='', app_name=''):
	shell_commands = {
		"install_app": "bench --site "+ docname + " install-app "+app_name,
		"remove_app": "bench --site "+ docname + " uninstall-app "+app_name+" --yes",
		"backup_site": "bench --site "+ docname + " backup --with-files",
		"migrate": "bench --site "+ docname + " migrate",
		"reinstall": "bench --site "+ docname + " reinstall --yes",
		"update": "bench update"
	}
	str_to_exec = [shell_commands[bench_command]]
	frappe.enqueue('bench_manager.bench_manager.doctype.bench_manager_command.bench_manager_command.run_command',
		exec_str_list=str_to_exec, cwd='..', doctype=doctype, key=key, docname=docname)