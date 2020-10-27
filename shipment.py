from flask import Blueprint, render_template, current_app, abort, g, \
    url_for, request, session, send_file
from galatea.tryton import tryton
from galatea.utils import slugify
from galatea.helpers import login_required, customer_required
from flask_babel import gettext as _, lazy_gettext
from flask_paginate import Pagination
import tempfile

shipment = Blueprint('shipment', __name__, template_folder='templates')

DISPLAY_MSG = lazy_gettext('Displaying <b>{start} - {end}</b> of <b>{total}</b>')

LIMIT = current_app.config.get('TRYTON_PAGINATION_SHIPMENT_LIMIT', 20)
STATE_EXCLUDE = current_app.config.get('TRYTON_SHIPMENT_OUT_STATE_EXCLUDE', [])

ShipmentOut = tryton.pool.get('stock.shipment.out')
ShipmentOutReturn = tryton.pool.get('stock.shipment.out.return')
DeliveryNote = tryton.pool.get('stock.shipment.out.delivery_note', type='report')

@shipment.route("/print/<int:id>", endpoint="delivery_note")
@login_required
@customer_required
@tryton.transaction()
def delivery_note(lang, id):
    '''Delivery Note Print'''

    domain = [('id', '=', id)]
    if not session.get('manager', False):
        domain.append(('customer', '=', session['customer']))
    shipments = ShipmentOut.search(domain, limit=1)

    if not shipments:
        abort(404)

    shipment, = shipments

    _, report, _, _ = DeliveryNote.execute([shipment.id], {})
    report_name = 'delivery-note-%s.pdf' % (slugify(shipment.number) or 'delivery-note')

    with tempfile.NamedTemporaryFile(
            prefix='%s-' % current_app.config['TRYTON_DATABASE'],
            suffix='.pdf', delete=False) as temp:
        temp.write(report)
    temp.close()
    data = open(temp.name, 'rb')

    return send_file(data, attachment_filename=report_name, as_attachment=True)

@shipment.route("/out/", endpoint="shipments-out")
@login_required
@customer_required
@tryton.transaction()
def shipment_out_list(lang):
    '''Customer Shipments'''

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    domain = [
        ('customer', '=', session['customer']),
        ('state', 'not in', STATE_EXCLUDE),
        ]
    total = ShipmentOut.search_count(domain)
    offset = (page-1)*LIMIT

    order = [
        ('id', 'DESC'),
        ]
    shipments = ShipmentOut.search(domain, offset, LIMIT, order)

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

@shipment.route("/out/<int:id>", endpoint="shipment-out")
@login_required
@customer_required
@tryton.transaction()
def shipment_out_detail(lang, id):
    '''Customer Shipment Detail'''

    shipments = ShipmentOut.search([
        ('id', '=', id),
        ('customer', '=', session['customer']),
        ('state', 'not in', STATE_EXCLUDE),
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
        'name': shipment.number or '#%s' % shipment.id,
        }]

    return render_template('shipment-out.html',
            breadcrumbs=breadcrumbs,
            shipment=shipment,
            )

@shipment.route("/out-return/", endpoint="shipments-out-return")
@login_required
@customer_required
@tryton.transaction()
def shipment_out_return_list(lang):
    '''Customer Return Shipments'''

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    domain = [
        ('customer', '=', session['customer']),
        ('state', 'not in', STATE_EXCLUDE),
        ]
    total = ShipmentOutReturn.search_count(domain)
    offset = (page-1)*LIMIT

    order = [
        ('id', 'DESC'),
        ]
    shipments = ShipmentOutReturn.search(domain, offset, LIMIT, order)

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

@shipment.route("/out-return/<int:id>", endpoint="shipment-out-return")
@login_required
@customer_required
@tryton.transaction()
def shipment_out_return_detail(lang, id):
    '''Shipment Out Return Detail'''

    shipments = ShipmentOutReturn.search([
        ('id', '=', id),
        ('customer', '=', session['customer']),
        ('state', 'not in', STATE_EXCLUDE),
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
        'name': shipment.number or '#%s' % shipment.id,
        }]

    return render_template('shipment-out-return.html',
            breadcrumbs=breadcrumbs,
            shipment=shipment,
            )

@shipment.route("/", endpoint="shipments")
@login_required
@customer_required
@tryton.transaction()
def shipment_list(lang):
    '''Shipments'''

    # Out / Out Return Shipments
    domain = [
        ('customer', '=', session['customer']),
        ('state', 'not in', STATE_EXCLUDE),
        ]
    out_shipments = ShipmentOut.search(domain, limit=LIMIT)
    out_return_shipments = ShipmentOutReturn.search(domain, limit=LIMIT)

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
