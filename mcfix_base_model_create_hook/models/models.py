# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models


class Base(models.AbstractModel):
    _inherit = 'base'

    def _share_company_with_parent(
            self, vals, parent_model, parent_vals):
        parent = parent_vals
        # share the company_id to the parent_id if possible
        if 'company_id' in vals and self.env[parent_model]._fields.\
                get('company_id'):
            parent['company_id'] = vals['company_id']
        return parent
