# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from subprocess import check_output, Popen, PIPE

class RunCommand(Document):
	pass

@frappe.whitelist()
def run_command(exec_str_list, cwd, doctype, key, docname=' '):
	exec_once = True
	console_dump = ''
	for str_to_exec in exec_str_list:
		if exec_once:
			terminal = Popen(str_to_exec.split(), stdin=PIPE, stdout=PIPE, cwd=cwd)
			exec_once = False
		else:
			terminal = terminal.communicate(str_to_exec.split(), stdin=PIPE, stdout=PIPE, cwd=cwd)
		for c in iter(lambda: terminal.stdout.read(1), ''):
			frappe.publish_realtime(key, c, user=frappe.session.user)
			console_dump += c

	doc = frappe.get_doc({'doctype': 'Run Command', 'source': doctype+': '+docname,
		 'command': '\n'.join(exec_str_list), 'console': console_dump})
	doc.insert()

	return terminal