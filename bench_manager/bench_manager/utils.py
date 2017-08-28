# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import Popen, check_output, PIPE, STDOUT

@frappe.whitelist()
def console_command(doctype='', docname='', key='', bench_command='', app_name=''):
	shell_commands = {
		"install_app": "bench --site "+ docname + " install-app "+app_name,
		"remove_app": "bench --site "+ docname + " uninstall-app "+app_name+" --yes",
		"backup_site": "bench --site "+ docname + " backup --with-files",
		"migrate": "bench --site "+ docname + " migrate",
		"reinstall": "bench --site "+ docname + " reinstall --yes",
		"update": "bench update",
		"new-site": "bench new-site "+docname,
		"drop-site": "bench drop-site "+docname #not-used
	}
	str_to_exec = [shell_commands[bench_command]]
	frappe.enqueue('bench_manager.bench_manager.utils.run_command',
		exec_str_list=str_to_exec, cwd='..', doctype=doctype, key=key, docname=docname)

@frappe.whitelist()
def run_command(exec_str_list, cwd, doctype, key, docname=' '):
	start_time = frappe.utils.time.time()
	exec_once = True
	console_dump = ''
	doc = frappe.get_doc({'doctype': 'Bench Manager Command', 'key': key, 'source': doctype+': '+docname,
		 'command': '\n'.join(exec_str_list), 'console': console_dump, 'status': 'Ongoing'})
	doc.insert()
	frappe.db.commit()

	try:
		doc = frappe.get_doc('Bench Manager Command', key)
		print exec_str_list
		for str_to_exec in exec_str_list:
			if exec_once:
				terminal = Popen(str_to_exec.split(), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cwd)
				exec_once = False
			else:
				terminal = terminal.communicate(str_to_exec)

			for c in iter(lambda: terminal.stdout.read(1), ''):
				frappe.publish_realtime(key, c, user=frappe.session.user)
				console_dump += c

		time_taken = frappe.utils.time.time() - start_time
		if terminal.wait():
			frappe.set_value('Bench Manager Command', key, 'status', 'Failed')
			frappe.publish_realtime(key, '\n\nFailed!\nThe operation took '+str(time_taken)+' seconds', user=frappe.session.user)
		else:
			frappe.set_value('Bench Manager Command', key, 'status', 'Success')
			frappe.publish_realtime(key, '\n\nSuccess!\nThe operation took '+str(time_taken)+' seconds', user=frappe.session.user)

		final_console_dump = ''
		console_dump = console_dump.split('\n\r')
		for i in console_dump:
			i = i.split('\r')
			final_console_dump += '\n'+i[-1]
					
		frappe.set_value('Bench Manager Command', key, 'console', final_console_dump)
		frappe.set_value('Bench Manager Command', key, 'time_taken', str(time_taken)+' seconds')
	except:
		frappe.set_value('Bench Manager Command', key, 'status', 'Failed')