# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import Popen, check_output, PIPE, STDOUT
import shlex


@frappe.whitelist()
def console_command(doctype='', docname='', key='', commands='', cwd='..'):
	commands = commands.split('\r')
	frappe.enqueue('bench_manager.bench_manager.utils.run_command',
		commands=commands, cwd=cwd, doctype=doctype, key=key, docname=docname)

@frappe.whitelist()
def run_command(commands, cwd, doctype, key, docname=' ', shell=False, after_command=None):
	start_time = frappe.utils.time.time()
	console_dump = ''
	doc = frappe.get_doc({'doctype': 'Bench Manager Command', 'key': key, 'source': doctype+': '+docname,
		 'command': ' && '.join(commands), 'console': console_dump, 'status': 'Ongoing'})
	doc.insert()
	frappe.db.commit()
	frappe.publish_realtime(key, "Executing Command:\n"+' && '.join(commands)+"\n\n", user=frappe.session.user)
	try:
		print commands
		for command in commands:
			if shell == False:
				terminal = Popen(shlex.split(command), shell=shell, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cwd)
			else:
				terminal = Popen(command, shell=shell, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cwd)
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
			doctype=doctype, docname=docname, commands=commands)

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

def _refresh(doctype, docname, commands):
	frappe.get_doc(doctype, docname).run_method('after_command', commands=commands)