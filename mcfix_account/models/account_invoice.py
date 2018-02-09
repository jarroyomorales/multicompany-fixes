from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(AccountInvoice, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.multi
    @api.onchange('company_id')
    def onchange_company_id(self):
        for invoice in self:
            if invoice.company_id and invoice.journal_id.company_id and \
                    invoice.journal_id.company_id != invoice.company_id:
                invoice.journal_id = self.env['account.journal'].search(
                    [('company_id', '=', invoice.company_id.id),
                     ('type', '=', invoice.journal_id.type)
                     ], limit=1)
            for line in invoice.invoice_line_ids:
                line.change_company_id()

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        addr = self.partner_id.address_get(['delivery'])
        self.fiscal_position_id = self.env['account.fiscal.position']. \
            with_context(force_company=self.company_id.id). \
            get_fiscal_position(self.partner_id.id,
                                delivery_id=addr['delivery'])

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.partner_id.company_id and \
                self.partner_id.company_id != self.company_id:
            self._cache.update(self._convert_to_cache(
                {'partner_id': False}, update=True))
        if self.company_id and self.refund_invoice_id.company_id and \
                self.refund_invoice_id.company_id != self.company_id:
            self.refund_invoice_id = False
        if self.company_id and self.payment_term_id.company_id and \
                self.payment_term_id.company_id != self.company_id:
            if self.refund_invoice_id.payment_term_id:
                self.payment_term_id = self.refund_invoice_id.payment_term_id
            else:
                self.payment_term_id = False
        if self.company_id and self.fiscal_position_id.company_id and \
                self.fiscal_position_id.company_id != self.company_id:
            if self.refund_invoice_id.fiscal_position_id:
                self.fiscal_position_id = \
                    self.refund_invoice_id.fiscal_position_id
            else:
                self.fiscal_position_id = False
        if self.company_id and self.move_id.company_id and \
                self.move_id.company_id != self.company_id:
            if self.refund_invoice_id.move_id:
                self.move_id = self.refund_invoice_id.move_id
            else:
                self.move_id = False
        if self.company_id and self.account_id.company_id and \
                self.account_id.company_id != self.company_id:
            if self.refund_invoice_id.account_id:
                self.account_id = self.refund_invoice_id.account_id
            else:
                self._cache.update(self._convert_to_cache(
                    {'account_id': False}, update=True))
        if self.company_id and self.partner_bank_id.company_id and \
                self.partner_bank_id.company_id != self.company_id:
            if self.refund_invoice_id.partner_bank_id:
                self.partner_bank_id = self.refund_invoice_id.partner_bank_id
            else:
                self.partner_bank_id = False
        if self.company_id and self.payment_ids:
            self.payment_ids = self.env['account.payment'].search(
                [('invoice_ids', 'in', [self.id]),
                 ('company_id', '!=', False),
                 ('company_id', '!=', self.company_id.id)])

    @api.multi
    @api.constrains('company_id', 'payment_term_id')
    def _check_company_id_payment_term_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.payment_term_id.company_id and\
                    rec.company_id != rec.payment_term_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Payment Term must be the same.'))

    @api.multi
    @api.constrains('company_id', 'fiscal_position_id')
    def _check_company_id_fiscal_position_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.fiscal_position_id.company_id and\
                    rec.company_id != rec.fiscal_position_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Fiscal Position must be the same.'))

    @api.multi
    @api.constrains('company_id', 'payment_ids')
    def _check_company_id_payment_ids(self):
        for rec in self.sudo():
            for line in rec.payment_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Account Invoice and in '
                          'Account Payment (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'refund_invoice_id')
    def _check_company_id_refund_invoice_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.refund_invoice_id.company_id and\
                    rec.company_id != rec.refund_invoice_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'move_id')
    def _check_company_id_move_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.move_id.company_id and\
                    rec.company_id != rec.move_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Move must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_id.company_id and\
                    rec.company_id != rec.account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_bank_id')
    def _check_company_id_partner_bank_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_bank_id.company_id and\
                    rec.company_id != rec.partner_bank_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Res Partner Bank must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Journal must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.search(
                    [('refund_invoice_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Invoice is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice.line'].search(
                    [('invoice_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Invoice is assigned to '
                          'Account Invoice Line (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.invoice.tax'].search(
                    [('invoice_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Invoice is assigned to Account Invoice Tax '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.move.line'].search(
                    [('invoice_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Invoice is assigned to Account Move Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.payment'].search(
                    [('invoice_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Invoice is assigned to Account Payment '
                          '(%s).' % field.name_get()[0][1]))


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def change_company_id(self):
        part = self.invoice_id.partner_id
        invoice_type = self.invoice_id.type
        company_id = self.invoice_id.company_id.id
        if part.lang:
            product = self.product_id.with_context(lang=part.lang)
        else:
            product = self.product_id
        account = self.get_invoice_line_account(
            invoice_type,
            product.with_context(force_company=company_id),
            self.invoice_id.fiscal_position_id,
            self.invoice_id.company_id)
        if account:
            self.account_id = account.id
        self._set_taxes()

    @api.v8
    def get_invoice_line_account(self, type, product, fpos, company):
        return super(AccountInvoiceLine, self.with_context(
            force_company=company.id)).get_invoice_line_account(
            type, product, fpos, company)

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_analytic_id.company_id and\
                    rec.company_id != rec.account_analytic_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_line_tax_ids')
    def _check_company_id_invoice_line_tax_ids(self):
        for rec in self.sudo():
            for line in rec.invoice_line_tax_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Account Invoice Line and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'invoice_id')
    def _check_company_id_invoice_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.invoice_id.company_id and\
                    rec.company_id != rec.invoice_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_id.company_id and\
                    rec.company_id != rec.account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Account Account must be the same.'))


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    @api.multi
    @api.constrains('company_id', 'tax_id')
    def _check_company_id_tax_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.tax_id.company_id and\
                    rec.company_id != rec.tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Tax and in '
                      'Account Tax must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_id')
    def _check_company_id_invoice_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.invoice_id.company_id and\
                    rec.company_id != rec.invoice_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Tax and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_id.company_id and\
                    rec.company_id != rec.account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Tax and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_analytic_id.company_id and\
                    rec.company_id != rec.account_analytic_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Tax and in '
                      'Account Analytic Account must be the same.'))
