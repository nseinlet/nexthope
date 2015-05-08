# -*- coding: utf-8 -*-
from openerp import http

# class NexthopeXls(http.Controller):
#     @http.route('/nexthope_xls/nexthope_xls/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nexthope_xls/nexthope_xls/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nexthope_xls.listing', {
#             'root': '/nexthope_xls/nexthope_xls',
#             'objects': http.request.env['nexthope_xls.nexthope_xls'].search([]),
#         })

#     @http.route('/nexthope_xls/nexthope_xls/objects/<model("nexthope_xls.nexthope_xls"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nexthope_xls.object', {
#             'object': obj
#         })