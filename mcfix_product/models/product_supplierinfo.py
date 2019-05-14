from odoo import api, models, _
from odoo.exceptions import ValidationError


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if 'company_id' not in val:
                if 'name' in val:
                    partner = self.env['res.partner'].browse([val['name']])
                    val['company_id'] = partner.company_id.id
                else:
                    val['company_id'] = False
        return super(SupplierInfo, self).create(vals)

    @api.multi
    @api.constrains('company_id', 'product_tmpl_id')
    def _check_company_id_product_tmpl_id(self):
        for rec in self.sudo():
            if not rec.product_tmpl_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Product Supplierinfo and in '
                      'Product Template must be the same.'))

    @api.multi
    @api.constrains('company_id', 'name')
    def _check_company_id_name(self):
        for rec in self.sudo():
            if not rec.name.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Product Supplierinfo and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if not rec.product_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Product Supplierinfo and in '
                      'Product Product must be the same.'))