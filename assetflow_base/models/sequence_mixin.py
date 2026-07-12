# -*- coding: utf-8 -*-
from odoo import models, api

class AssetflowSequenceMixin(models.AbstractModel):
    _name = 'assetflow.sequence.mixin'
    _description = 'AssetFlow Sequence Mixin'

    @api.model
    def _get_next_sequence(self, sequence_code):
        """
        Helper method to get the next sequence value for a given sequence code.
        Returns '/' if the sequence is not found.
        """
        return self.env['ir.sequence'].next_by_code(sequence_code) or '/'
