from flask import Blueprint, render_template, current_app, abort, g, \
    url_for, request, session
from galatea.tryton import tryton
from galatea.helpers import login_required
from flask.ext.babel import gettext as _, lazy_gettext
from flask.ext.paginate import Pagination

shipment = Blueprint('shipment', __name__, template_folder='templates')

DISPLAY_MSG = lazy_gettext('Displaying <b>{start} - {end}</b> of <b>{total}</b>')

LIMIT = current_app.config.get('TRYTON_PAGINATION_SHIPMENT_LIMIT', 20)

ShipmentOut = tryton.pool.get('stock.shipment.out')
ShipmentOutReturn = tryton.pool.get('stock.shipment.out.return')

SHIPMENT_OUT_FIELD_NAMES = [
    'create_date', 'effective_date', 'planned_date', 'reference', 'code', 'state',
    ]
SHIPMENT_OUT_RETURN_FIELD_NAMES = [
    'create_date', 'effective_date', 'planned_date', 'reference', 'code', 'state',
    ]

@shipment.route("/out/", endpoint="shipments-out")
@login_required
@tryton.transaction()
def shipment_out_list(lang):
    '''Customer Shipments'''

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    domain = [
        ('customer', '=', session['customer']),
        ]
    total = ShipmentOut.search_count(domain)
    offset = (page-1)*LIMIT

    order = [
        ('id', 'DESC'),
        ]
    shipments = ShipmentOut.search_read(
        domain, offset, LIMIT, order, SHIPMENT_OUT_FIELD_NAMES)

    pagination = Pagination(
        page=page, total=total, per_page=LIMIT, display_msg=DISPLAY_MSG, bs_version='3')

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('my-account', lang=g.language),
        'name': _('My Account'),
        }, {
        'slug': url_for('.shipments', lang=g.language),
        'name': _('Shipments'),
        }, {
        'slug': url_for('.shipments-out', lang=g.language),
        'name': _('Customer Shipments'),
        }]

    return render_template('shipments-out.html',
            breadcrumbs=breadcrumbs,
            pagination=pagination,
            shipments=shipments,
            )

@shipment.route("/out/<id>", endpoint="shipment-out")
@login_required
@tryton.transaction()
def shipment_out_detail(lang, id):
    '''Customer Shipment Detail'''

    shipments = ShipmentOut.search([
        ('id', '=', id),
        ('customer', '=', session['customer']),
        ], limit=1)
    if not shipments:
        abort(404)

    shipment, = ShipmentOut.browse(shipments)

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('my-account', lang=g.language),
        'name': _('My Account'),
        }, {
        'slug': url_for('.shipments', lang=g.language),
        'name': _('Shipments'),
        }, {
        'slug': url_for('.shipments-out', lang=g.language),
        'name': _('Customer Shipments'),
        }, {
        'slug': url_for('.shipment-out', lang=g.language, id=shipment.id),
        'name': shipment.reference or _('Not reference'),
        }]

    return render_template('shipment-out.html',
            breadcrumbs=breadcrumbs,
            shipment=shipment,
            )

@shipment.route("/out-return/", endpoint="shipments-out-return")
@login_required
@tryton.transaction()
def shipment_out_return_list(lang):
    '''Customer Return Shipments'''

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    domain = [
        ('customer', '=', session['customer']),
        ]
    total = ShipmentOutReturn.search_count(domain)
    offset = (page-1)*LIMIT

    order = [
        ('id', 'DESC'),
        ]
    shipments = ShipmentOutReturn.search_read(
        domain, offset, LIMIT, order, SHIPMENT_OUT_RETURN_FIELD_NAMES)

    pagination = Pagination(
        page=page, total=total, per_page=LIMIT, display_msg=DISPLAY_MSG, bs_version='3')

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('my-account', lang=g.language),
        'name': _('My Account'),
        }, {
        'slug': url_for('.shipments', lang=g.language),
        'name': _('Shipments'),
        }, {
        'slug': url_for('.shipments-out-return', lang=g.language),
        'name': _('Customer Return Shipments'),
        }]

    return render_template('shipments-out-return.html',
            breadcrumbs=breadcrumbs,
            pagination=pagination,
            shipments=shipments,
            )

@shipment.route("/out-return/<id>", endpoint="shipment-out-return")
@login_required
@tryton.transaction()
def shipment_out_return_detail(lang, id):
    '''Shipment Out Return Detail'''

    shipments = ShipmentOutReturn.search([
        ('id', '=', id),
        ('customer', '=', session['customer']),
        ], limit=1)
    if not shipments:
        abort(404)

    shipment, = ShipmentOutReturn.browse(shipments)

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('my-account', lang=g.language),
        'name': _('My Account'),
        }, {
        'slug': url_for('.shipments', lang=g.language),
        'name': _('Shipments'),
        }, {
        'slug': url_for('.shipments-out-return', lang=g.language),
        'name': _('Customer Return Shipments'),
        }, {
        'slug': url_for('.shipment-out-return', lang=g.language, id=shipment.id),
        'name': shipment.reference or _('Not reference'),
        }]

    return render_template('shipment-out-return.html',
            breadcrumbs=breadcrumbs,
            shipment=shipment,
            )

@shipment.route("/", endpoint="shipments")
@login_required
@tryton.transaction()
def shipment_list(lang):
    '''Shipments'''

    # Out / Out Return Shipments
    domain = [
        ('customer', '=', session['customer']),
        ]
    out_shipments = ShipmentOut.search_read(
        domain, limit=LIMIT, fields_names=SHIPMENT_OUT_FIELD_NAMES)
    out_return_shipments = ShipmentOutReturn.search_read(
        domain, limit=LIMIT, fields_names=SHIPMENT_OUT_RETURN_FIELD_NAMES)

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('my-account', lang=g.language),
        'name': _('My Account'),
        }, {
        'slug': url_for('.shipments', lang=g.language),
        'name': _('Shipments'),
        }]

    return render_template('shipments.html',
            breadcrumbs=breadcrumbs,
            out_shipments=out_shipments,
            out_return_shipments=out_return_shipments,
            )
