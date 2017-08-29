# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json, os
from subprocess import check_output, Popen, PIPE

class BenchSettings(Document):
	site_config_fields = ["background_workers", "shallow_clone", "admin_password",
		"auto_email_id", "auto_update", "frappe_user", "global_help_setup",
		"dropbox_access_key", "dropbox_secret_key", "gunicorn_workers", "github_username",
		"github_password", "mail_login", "mail_password", "mail_port", "mail_server",
		"use_tls", "rebase_on_pull", "redis_cache", "redis_queue", "redis_socketio",
		"restart_supervisor_on_update", "root_password", "serve_default_site",
		"socketio_port", "update_bench_on_update", "webserver_port", "file_watcher_port"]

	def set_attr(self, varname, varval):
		return setattr(self, varname, varval)

	def onload(self):
		self.sync_site_config()

	def sync_site_config(self):
		common_site_config_path = 'common_site_config.json'
		with open(common_site_config_path, 'r') as f:
			common_site_config_data = json.load(f)
			for site_config_field in self.site_config_fields:
				try:
					self.set_attr(site_config_field,
						common_site_config_data[site_config_field])
				except:
					pass

@frappe.whitelist()
def sync_sites():
	site_dirs = update_site_list()
	site_entries = [x['name'] for x in frappe.get_all('Site')]
	create_sites = list(set(site_dirs) - set(site_entries))
	delete_sites = list(set(site_entries) - set(site_dirs))
	frappe.msgprint('Please be patitent while enries for these sites are created')
	frappe.msgprint(create_sites)
	for site in create_sites:
		doc = frappe.get_doc({'doctype': 'Site', 'site_name': site, 'developer_flag':1})
		doc.insert()
	frappe.msgprint('Please be patitent while enries for these sites are deleted')
	frappe.msgprint(delete_sites)
	for site in delete_sites:
		doc = frappe.get_doc('Site', site)
		doc.developer_flag = 1
		doc.save()
		doc.delete()
	frappe.msgprint('Done')

@frappe.whitelist()
def sync_apps():
	app_dirs = update_app_list()
	app_entries = [x['name'] for x in frappe.get_all('App')]
	create_apps = list(set(app_dirs) - set(app_entries))
	delete_apps = list(set(app_entries) - set(app_dirs))
	create_apps = filter(lambda a: a != '', create_apps)
	delete_apps = filter(lambda a: a != '', delete_apps)
	frappe.msgprint('Please be patitent while enries for these apps are created')
	frappe.msgprint(create_apps)
	for app in create_apps:
		doc = frappe.get_doc({'doctype': 'App', 'app_name': app,
			'app_description': 'lorem ipsum', 'app_publisher': 'lorem ipsum',
			'app_email': 'lorem ipsum', 'developer_flag':1})
		doc.insert()
	frappe.msgprint('Please be patitent while enries for these apps are deleted')
	frappe.msgprint(delete_apps)
	for app in delete_apps:
		doc = frappe.get_doc('App', app)
		doc.developer_flag = 1
		doc.save()
		doc.delete()
	frappe.msgprint('Done')

# def _bench_update(command, user):
# 	terminal = Popen(command.split(), stdout=PIPE, cwd='..')
# 	for c in iter(lambda: terminal.stdout.read(1), ''):
# 		frappe.publish_realtime('terminal_output', c, user=user)

def update_app_list():
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
	if '' in site_list:
		site_list.remove('')
	return site_list

@frappe.whitelist()
def sync_backups():
	backup_dirs_data = update_backup_list()
	backup_entries = [x['name'] for x in frappe.get_all('Site Backup')]
	bakcup_dirs = [x['site_name']+' '+x['date']+' '+x['time']  for x in backup_dirs_data]
	create_backups = list(set(bakcup_dirs) - set(backup_entries))
	delete_backups = list(set(backup_entries) - set(bakcup_dirs))
	frappe.msgprint('Please be patitent while enries for these backups are created')
	frappe.msgprint(create_backups)
	for sitename_date_time in create_backups:
		sitename_date_time = sitename_date_time.split(' ')
		backup = {}
		for x in backup_dirs_data:
			if (x['site_name'] == sitename_date_time[0] and
				x['date'] == ' '.join(sitename_date_time[1:4])  and
				x['time'] == sitename_date_time[4]):
				backup = x
				break
		doc = frappe.get_doc({'doctype': 'Site Backup',
			'site_name': backup['site_name'],
			'date': backup['date'], 'time': backup['time'],
			'stored_location': backup['stored_location'],
			'public_file_backup': backup['public_file_backup'],
			'private_file_backup': backup['private_file_backup'],
			'hash': backup['hash'],
			'file_path': backup['file_path'],
			'developer_flag': 1})
		doc.insert()
	frappe.msgprint('Please be patitent while enries for these sites are deleted')
	frappe.msgprint(delete_backups)
	for backup in delete_backups:
		doc = frappe.get_doc('Site Backup', backup)
		doc.developer_flag = 1
		doc.save()
		doc.delete()
	frappe.msgprint('Done')

def update_backup_list():
	all_sites = []
	archived_sites = []
	sites = []
	for root, dirs, files in os.walk("../archived_sites/", topdown=True):
		archived_sites.extend(dirs)
		break
	archived_sites = ["../archived_sites/"+x for x in archived_sites]
	all_sites.extend(archived_sites)
	for root, dirs, files in os.walk("../sites/", topdown=True):
		for site in dirs:
			files_list = check_output("cd ../sites/"+site+" && ls", shell=True).split("\n")
			if 'site_config.json' in files_list:
				sites.append(site)
		break
	sites = ["../sites/"+x for x in sites]
	all_sites.extend(sites)

	response = []

	backups = []
	for site in all_sites:
		backup_path = os.path.join(site, "private", "backups")
		try:
			backup_files = check_output("cd "+backup_path+" && ls *database.sql*",
				shell=True).strip('\n').split('\n')
			for backup_file in backup_files:
				inner_response = {}
				date_time_hash = backup_file.rsplit('_', 1)[0]
				file_path = backup_path+'/'+date_time_hash
				inner_response['site_name'] = site.split('/')[2]
				inner_response['date'] = get_date(date_time_hash)
				inner_response['time'] = get_time(date_time_hash)
				inner_response['stored_location'] = site.split('/')[1]
				inner_response['private_file_backup'] = os.path.isfile(backup_path+\
					'/'+date_time_hash+"_private_files.tar")
				inner_response['public_file_backup'] = os.path.isfile(backup_path+\
					'/'+date_time_hash+"_files.tar")
				inner_response['hash'] = get_hash(date_time_hash)
				inner_response['file_path'] = file_path[3:]
				response.append(inner_response)
		except:
			pass
			# frappe.msgprint('There are no backups to sync!')
	return response

def get_date(date_time_hash):
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
		'August', 'September', 'October', 'November', 'December']
	date = int(date_time_hash.split('_')[0])
	return str(date % 100) + ' ' +str(months[(date/100)%100 - 1]) + ' ' +\
		str(date / 10000)

def get_time(date_time_hash):
	time = date_time_hash.split('_')[1]
	return time[0:2]+':'+time[2:4]+':'+time[4:6]

def get_hash(date_time_hash):
	return date_time_hash.split('_')[2]

@frappe.whitelist()
def sync_all():
	sync_sites()
	sync_apps()
	sync_backups()
