# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate_Property_Type.Estate_Property_Type'

    name = fields.Char(required=True)
    





 