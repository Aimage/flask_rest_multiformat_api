# -*- coding: utf-8 -*-

from .utils import get_attr_names, get_primary_key_name
from .log import logger


def build_base_query(session, model):
    query = session.query(model)
    return query


def paginate(query, number_par_page, page_number):
    """we count page from 0"""
    offset_ = number_par_page * int(page_number)
    query = query.limit(number_par_page).offset(offset_)
    return query


def get_single(session, model, id):
    logger.debug(f"MODEL: {model} -session: {session} ID:  {id}")
    primary_kay_name = get_primary_key_name(model)
    primary_key_attrib = getattr(model, primary_kay_name)
    query = session.query(model)
    query = query.filter(primary_key_attrib == id)
    return query.first()


def apply_filters(query, model, filters):
    for _filter in filters:
        op = _filter.get('op')
        name = _filter.get('name')
        value = _filter.get('val')
        attrib = getattr(model, name, None)
        if not attrib:
            continue
        if op == 'eq':
            query = query.filter(attrib == value)
        if op == 'lt':
            query = query.filter(attrib < value)
        if op == 'le':
            query = query.filter(attrib <= value)
        if op == 'gt':
            query = query.filter(attrib > value)
        if op == 'ge':
            query = query.filter(attrib >= value)
        if op == 'like':
            value = value.replace('%', '')
            query = query.filter(attrib.like('%%%s%%' % value))
    return query


def apply_order(query, model, order_by, order):
    attrib = getattr(model, order_by, None)
    if attrib:
        if order == '1':
            query = query.order_by(attrib.desc())
        else:
            query = query.order_by(attrib)
    return query


def get_many(session,
             model,
             filters=[],
             order_by='',
             order='',
             number_par_page=50,
             page_number=0):
    query = build_base_query(session, model)
    query = apply_filters(query, model, filters)
    if order_by:
        query = apply_order(query, model, order_by, order)
    query = paginate(query, number_par_page, page_number)
    return query.all()
