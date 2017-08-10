# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json, os
from subprocess import check_output, Popen, PIPE

class Bench(Document):
	def validate(self):
		self.update_app_list()
		self.update_site_list()

	def update_app_list(self):
		self.app_list = '\n'.join(self.get_available_apps())

	def get_available_apps(self):
		app_list_file = 'apps.txt'
		with open(app_list_file, "r") as f:
			apps = f.read().split('\n')
		return apps

	def update_site_list(self):
		site_list = []
		for root, dirs, files in os.walk(".", topdown=True):
			for name in files:
				if name == 'site_config.json':
					site_list.append(str(root).strip('./'))
					break
		site_list.remove('')
		self.site_list = '\n'.join(site_list)

@frappe.whitelist()
def bench_update(command):
	frappe.enqueue('bench_manager.bench_manager.doctype.bench.bench._bench_update',
		command = command, user = frappe.session.user)

@frappe.whitelist()
def sync_sites(doctype):
	site_dirs = update_site_list()
	site_entries = [x['name'] for x in frappe.get_all('Site')]
	create_sites = list(set(site_dirs) - set(site_entries))
	delete_sites = list(set(site_entries) - set(site_dirs))
	frappe.msgprint('Please be patitent while enries for these sites are created')
	frappe.msgprint(create_sites)
	for site in create_sites:
		doc = frappe.get_doc({'doctype': 'Site', 'site_name': site, 'bypass_flag':1})
		doc.insert()
	frappe.msgprint('Please be patitent while enries for these sites are deleted')
	frappe.msgprint(delete_sites)
	for site in delete_sites:
		doc = frappe.get_doc('Site', site)
		doc.bypass_flag = 1
		doc.save()
		doc.delete()

@frappe.whitelist()
def sync_apps(doctype):
	frappe.msgprint('in python sync_apps')

def _bench_update(command, user):
	terminal = Popen(command.split(), stdout=PIPE, cwd='..')
	for c in iter(lambda: terminal.stdout.read(1), ''):
		frappe.publish_realtime('terminal_output', c, user=user)

def update_app_list():
	return '\n'.join(get_available_apps())

def get_available_apps():
	app_list_file = 'apps.txt'
	with open(app_list_file, "r") as f:
		apps = f.read().split('\n')
	return apps

def update_site_list():
	site_list = []
	for root, dirs, files in os.walk(".", topdown=True):
		for name in files:
			if name == 'site_config.json':
				site_list.append(str(root).strip('./'))
				break
	site_list.remove('')
	return site_list