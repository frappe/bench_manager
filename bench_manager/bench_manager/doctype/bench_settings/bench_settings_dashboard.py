from frappe import _

def get_data():
	return {
		'fieldname': 'bench_settings',
		'transactions': [
			{
				'label': _('Sites and Apps'),
				'items': ['Site', 'App']
			},
			{
				'label': _('Backups and Logs'),
				'items': ['Site Backup', 'Bench Manager Command']
			}
		]
	}