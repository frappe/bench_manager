# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import Popen, check_output, PIPE, STDOUT
import shlex

@frappe.whitelist()
def console_command(doctype='', docname='', key='', bench_command='', app_name='', branch_name='', cwd='..', after_command=None):
	shell_commands = {
		"install_app": ["bench --site "+ docname + " install-app " + app_name],
		"remove_app": ["bench --site "+ docname + " uninstall-app " + app_name + " --yes"],
		"backup_site": ["bench --site "+ docname + " backup --with-files"],
		"migrate": ["bench --site "+ docname + " migrate"],
		"reinstall": ["bench --site "+ docname + " reinstall --yes"],
		"update": ["bench update"],
		"new-site": ["bench new-site "+docname],
		"drop-site": ["bench drop-site "+docname],
		"switch-to-branch": ["git checkout "+branch_name],
		"create-branch": ["git branch "+branch_name],
		"delete-branch": ["git branch -D "+branch_name],
		"git-init": ["git init", "git add .", "git commit -m 'Initial Commit'"],
		"git-fetch": ["git fetch --all"],
		"new-site & install-erpnext": ["bench new-site "+docname,
			"bench --site "+docname+" install-app erpnext"],
		"new-site & get-app & install-erpnext": ["bench new-site "+docname,
			"bench get-app erpnext https://github.com/frappe/erpnext.git","bench --site "+docname+" install-app erpnext"]
	}
	exec_str_list = shell_commands[bench_command]
	frappe.enqueue('bench_manager.bench_manager.utils.run_command',
		exec_str_list=exec_str_list, cwd=cwd, doctype=doctype, key=key, docname=docname, after_command=after_command)

@frappe.whitelist()
def run_command(exec_str_list, cwd, doctype, key, docname=' ', shell=False, after_command=None):
	start_time = frappe.utils.time.time()
	console_dump = ''
	doc = frappe.get_doc({'doctype': 'Bench Manager Command', 'key': key, 'source': doctype+': '+docname,
		 'command': ' && '.join(exec_str_list), 'console': console_dump, 'status': 'Ongoing'})
	doc.insert()
	frappe.db.commit()
	try:
		print exec_str_list
		for str_to_exec in exec_str_list:
			if shell == False:
				terminal = Popen(shlex.split(str_to_exec), shell=shell, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cwd)
			else:
				terminal = Popen(str_to_exec, shell=shell, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cwd)
			for c in iter(lambda: terminal.stdout.read(1), ''):
				frappe.publish_realtime(key, c, user=frappe.session.user)
				console_dump += c
		if terminal.wait():
			_close_the_doc(start_time, key, console_dump, status='Failed', user=frappe.session.user)
		else:
			_close_the_doc(start_time, key, console_dump, status='Success', user=frappe.session.user)
	except:
		_close_the_doc(start_time, key, console_dump, status='Failed', user=frappe.session.user)
	finally:
		frappe.db.commit()
		# hack: frappe.db.commit() to make sure the log created is robust,
		# and the _refresh throws an error if the doc is deleted 
		frappe.enqueue('bench_manager.bench_manager.utils._refresh',
			doctype=doctype, docname=docname, exec_str_list=exec_str_list)

def _close_the_doc(start_time, key, console_dump, status, user):
	time_taken = frappe.utils.time.time() - start_time
	final_console_dump = ''
	console_dump = console_dump.split('\n\r')
	for i in console_dump:
		i = i.split('\r')
		final_console_dump += '\n'+i[-1]
	frappe.set_value('Bench Manager Command', key, 'console', final_console_dump)
	frappe.set_value('Bench Manager Command', key, 'status', status)
	frappe.set_value('Bench Manager Command', key, 'time_taken', time_taken)
	frappe.publish_realtime(key, '\n\n'+status+'!\nThe operation took '+str(time_taken)+' seconds', user=user)

def _refresh(doctype, docname, exec_str_list):
	frappe.get_doc(doctype, docname).run_method('after_command', commands=exec_str_list)