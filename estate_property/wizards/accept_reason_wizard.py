
# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError





class AcceptReasonWizard(models.TransientModel):
    _name = 'accept.reason.wizard'
    _description = 'accept_reason_wizard'
    
    reason = fields.Text()
    date = fields.Date(default=fields.Date.context_today)
    property_id = fields.Many2one('estate.property')
    offer_id = fields.Many2one('estate.property.offer')



    def action_accept(self):
        for rec in self:
            rec.property_id.write({
                'selling_price': rec.offer_id.price,
                'buyer' : rec.offer_id.partner_id.id,
                'state' : 'offer_accepted',
                'offer_accept_reason' : rec.reason,
                'offer_accept_date' : rec.date,

            })
            rec.offer_id.status = 'accepted'