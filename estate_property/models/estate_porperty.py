



# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError

from random import randint





class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'


    name = fields.Char(required=True)
    description = fields.Text()
    description2 = fields.Text(readonly=True, default='''NOTE: Should you wish to switch to a different currency, we recommend visiting our currency                             
    exchange service for a hassle-free currency conversion. Your satisfaction is our top priority!''')

    postcode = fields.Char()
    date_availibility = fields.Date(copy=False, default=lambda self: date.today() + timedelta(days=90))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float( copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),

    ])
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
    ], default='new'
    )
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    property_type_id = fields.Many2one('estate.property.type', required=True)
    tag_ids = fields.Many2many('estate.property.tag')
    buyer = fields.Many2one('res.partner')
    salesman = fields.Many2one('res.users', default=lambda self: self.env.user)
    total_area = fields.Float(compute='_compute_total_area')
    best_price = fields.Float(compute='_compute_best_price')

    _sql_constraints = [
        (
            'expected_price_positive',
            'CHECK(expected_price >= 0)',
            'Expected price must be greater than 0.'
        ),
        (
            'selling_price_positive',
            'CHECK(selling_price >= 0)',
            'Selling price must be greater than 0.'
        ),
    ]

    # @api.ondelete(at_uninstall=False)
    # def _unlink_if_state_new_cancel(self):
    #     if self.state not in ('new', 'cancelled'):
    #         raise ValidationError('Record can only be deleted in new or cancel states.')

    


    

    amount_in_usd = fields.Float()
    amount_in_afn = fields.Float()
    
    total_in_afn = fields.Float(compute="compute_total_in_afn")
    total_in_usd = fields.Float(compute="compute_total_in_usd")
    exchange_rate =fields.Float()




    @api.depends('amount_in_usd', 'exchange_rate',)
    def compute_total_in_afn(self):
        for rec in self:
            rec.total_in_afn = rec.amount_in_usd * rec.exchange_rate

    @api.depends('amount_in_afn', 'exchange_rate')
    def compute_total_in_usd(self):
        for rec in self:
            rec.total_in_usd = False
            if rec.exchange_rate > 0:
                rec.total_in_usd = rec.amount_in_afn / rec.exchange_rate

    def unlink(self):
        for rec in self:
            if rec.state not in ('new', 'cancelled'):
                raise ValidationError('Record can only be deleted in new or cancel states.')
            
            return super(EstateProperty, self).unlink()
            
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price < record.expected_price * 0.9:
                raise ValidationError('Selling price should be at least 90% expected price.')
            
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for rec in self:
            rec.best_price = False
            if rec.offer_ids:
                best_price = max(rec.offer_ids.mapped('price'))
                rec.best_price = best_price

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 10
        else:
            self.garden_orientation = False
            self.garden_area = False

    def action_sold(self):
        for rec in self:
            if rec.state == 'cancelled' :
                raise UserError('Cancelled property cannot be sold.')
            rec.state = 'sold'

    def action_cancel(self):
        for rec in self:
            rec.write({
                'state': 'cancelled'
            })


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'name'

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')
    sequence = fields.Integer()
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute='_compute_offer_count')

    def open_offers(self):
        for rec in self:
            return {
                'name': 'Offers',
                'type': 'ir.actions.act_window',
                # 'view_type': 'form,tree',
                'view_mode': 'tree,form',
                'res_model': 'estate.property.offer',
                'domain': [('property_type_id', '=', rec.id)],
            }

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    _sql_constraints = [
        (
            'unq_name',
            'unique(name)',
            'Property type name already exist'
        ),
    ]


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = 'name'

    def _default_color(self):
        return randint(1, 11)
    
    name = fields.Char(required=True)
    color = fields.Integer(default=lambda self: self._default_color())

    _sql_constraints = [
        (
            'unq_name',
            'unique(name)',
            'Property tag name already exist'
        ),
    ]



class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'
    _rec_name='partner_id'

    price = fields.Float()
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], copy=False
    )
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True, ondelete='cascade')
    validty = fields.Integer()
    date_deadline = fields.Date(compute='_compute_date_deadline')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

    _sql_constraints = [
        (
            'price_positive',
            'CHECK(price > 0)',
            'Price must be greater than 0.'
        ),
    ]

    @api.model
    def create(self, values):
        estate_property = self.env['estate.property'].browse(values.get('property_id'))
        estate_property.state = 'offer_received'
        if values.get('price') <= estate_property.best_price:
            raise ValidationError(f"The offer must be higher than {estate_property.best_price}")
        res = super(EstatePropertyOffer, self).create(values)
        # res.property_id.state = 'offer_received'
        return res

    

    @api.depends('validty', 'create_date')
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = rec.create_date + timedelta(days=rec.validty) if rec.create_date else False

    def action_accept(self):
        for rec in self:
            rec.property_id.selling_price = rec.price
            rec.property_id.buyer = rec.partner_id.id
            rec.status = 'accepted'

    def action_refuse(self):
        for rec in self:
            rec.status = 'refused'










# # -*- coding: utf-8 -*-

# from odoo import models, fields, api
# from odoo.exceptions import ValidationError



# class EstateProperty(models.Model):
#     _name = 'estate.property'
#     _description = 'estate_property.estate_property'

#     name = fields.Char(required=True)
#     description = fields.Text()
#     postcode = fields.Char()
#     date_availability = fields.Date()
#     expected_price = fields.Float(required=True)
#     selling_price = fields.Float()
#     bedrooms = fields.Integer()
#     living_area = fields.Integer()
#     facades = fields.Integer()
#     garage = fields.Boolean()
#     garden = fields.Boolean()
#     garden_area = fields.Integer()
#     availability_from = fields.Date()
#     garden_orientation = fields.Selection([
#         ('north', 'North'),
#         ('south', 'South'),
#         ('east' , 'East '),
#         ('west' , 'West' ),
#     ])
#     state = fields.Selection([
#         ('accepted', 'Accepted'),
#         ('refused', 'Refused'),
#         ('new', 'New'),
#         ('open_order', 'Open Order'),
#         ('closed_order', 'Closed Order'),
#         ('sold_order', 'Sold Order'),
#     ])

#     property_type_id = fields.Many2one('estate.property.type')
#     property_tag_ids = fields.Many2many('estate.property.tag')
#     property_offer_ids = fields.One2many('estate.property.offer','property_id')


#     total_area = fields.Integer(compute="_compute_total_area")

#     @api.depends('living_area', 'garden_area')
#     def _compute_total_area(self):
#         for rec in self:
#             rec.total_area = rec.living_area + rec.garden_area

#     @api.onchange('garden')
#     def _onchange_garden(self):
#         if self.garden:
#             self.garden_area = 10
#             self.garden_orientation = 'north'
#         else:
#             self.garden_area = 0
#             self.garden_orientation = False
    

#     amount_in_usd = fields.Float()
#     amount_in_afn = fields.Float()
    

#     total_in_afn = fields.Float(compute="compute_total_in_afn")
#     total_in_usd = fields.Float(compute="compute_total_in_usd")
#     exchange_rate =fields.Float()

#     @api.depends('amount_in_usd', 'exchange_rate',)
#     def compute_total_in_afn(self):
#         for rec in self:
#             rec.total_in_afn = rec.amount_in_usd * rec.exchange_rate

#     @api.depends('amount_in_afn', 'exchange_rate')
#     def compute_total_in_usd(self):
#         for rec in self:
#             rec.total_in_usd = False
#             if rec.exchange_rate > 0:
#                 rec.total_in_usd = rec.amount_in_afn / rec.exchange_rate


#     _sql_constraints = [
#         (
#             'expected_price_positive',
#             'CHECK(expected_price >= 0)',
#             'Expected price must be greater than 0.'
#         ),
#         (
#             'selling_price_positive',
#             'CHECK(selling_price >= 0)',
#             'Selling price must be greater than 0.'
#         ),
#     ]



    

#     # num1 = fields.Integer()
#     # num2 = fields.Integer()
#     # total = fields.Integer(compute="_compute_total")


#     # @api.depends('num1', 'num2')
#     # def _compute_total(self):
#     #     # self.total = self.num1 + self.num2
#     #     for rec in self:
#     #         rec.total = rec.num1 + rec.num2








