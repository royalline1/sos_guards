import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ReportUniformProjectSpecific(models.AbstractModel):
	_name = 'report.sos_uniform.report_uniformprojectspecific'
	_description = 'Specific Project Uniform Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	def get_project_centers(self, project_id):
		self.env.cr.execute("select distinct center_id from sos_post pp, res_partner p where pp.id = p.id and p.active = True and project_id = %s"%project_id)
		rec_ids = self.env.cr.dictfetchall()

		center_ids = []
		for rec in rec_ids:
			center_ids.append(rec['center_id'])
		centers = self.env['sos.center'].search([('id','in',center_ids)])	
		return centers
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		state = data['form']['state'] and data['form']['state']
		project_id = data['form']['project_id'] and data['form']['project_id'][0]
		res = []
		
		centers = self.get_project_centers(project_id)
		
		if centers:
			for center in centers:
				dom = []
				dom = [('date', '>=', date_from), ('date', '<=', date_to),('project_id', '=', project_id)]
				
				if state in ['draft','open','review','approve','dispatch','done','reject','cancel']:
					dom += [('state', '=', state)]
				elif state == 'dispatch_deliver':
					dom += [('state', 'in', ['dispatch','done'])]	
				elif state == 'none_dispatched':
					dom += [('state', 'in', ['open','review','approve'])]
				elif state == 'all':
					dom += [('state', 'in', ['open','review','approve','dispatch','done','reject','cancel'])]
					
				demands = self.env['sos.uniform.demand'].search(dom)
				if demands:
					res.append({
						'center_name' : center.name,
						'demands': demands,
						})
			
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_uniformprojectspecific')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Project" : res or False,
			"get_date_formate" : self.get_date_formate,
		}
		
