# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate_Property_tag.Estate_Property_tag'

    name = fields.Char(required=True)
    





 