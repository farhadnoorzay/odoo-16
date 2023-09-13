# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'estate_property.estate_property'

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date()
    expected_price = fields.Float(required=True)
    selling_price = fields.Float()
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    availability_from = fields.Date()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east' , 'East '),
        ('west' , 'West' ),
    ])
    state = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
        ('new', 'New'),
        ('open_order', 'Open Order'),
        ('closed_order', 'Closed Order'),
        ('sold_order', 'Sold Order'),
    ])

    property_type_id = fields.Many2one('estate.property.type')
    property_tag_ids = fields.Many2many('estate.property.tag')
    property_offer_ids = fields.One2many('estate.property.offer','property_id')




 