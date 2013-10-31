#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

from django.template import RequestContext
from django.shortcuts import render_to_response

from paypal.standard.pdt.models import PayPalPDT
from paypal.standard.pdt.forms import PayPalPDTForm


LOGGER = logging.getLogger(__name__)


def pdt(request, item_check_callable=None, template="pdt/pdt.html",
        context=None):
    """Payment data transfer implementation: http://tinyurl.com/c9jjmw"""

    LOGGER.debug(">> Paypal's notification request: method=%s" %
                 request.method)
    LOGGER.debug("GET=%s" % repr(request.GET))
    LOGGER.debug("POST=%s" % repr(request.POST))

    context = context or {}
    pdt_obj = None

    txn_id = getattr(request, request.method).get('txn_id', None)
    LOGGER.info("PDT transaction id: %s" % repr(txn_id))

    failed = False

    if txn_id is not None:
        # If an existing transaction with the id tx exists: use it
        try:
            pdt_obj = PayPalPDT.objects.get(txn_id=txn_id)
        except PayPalPDT.DoesNotExist:
            LOGGER.debug("This is a new transaction so we continue processing "
                         "PDT request")

        if pdt_obj is None:
            form = PayPalPDTForm(getattr(request, request.method))
            if form.is_valid():
                try:
                    pdt_obj = form.save(commit=False)
                    pdt_obj.tx = txn_id  # backward compatibillity
                except Exception, e:
                    LOGGER.exception("Exception creating PDT object from "
                                     "formulary:")
                    error = repr(e)
                    failed = True
            else:
                error = form.errors
                failed = True

            if failed:
                pdt_obj = PayPalPDT()
                pdt_obj.set_flag("Invalid form. %s" % error)
                LOGGER.warn("PDT validation has failed: %s" % error)

            pdt_obj.initialize(request)

            if not failed:
                # The PDT object gets saved during verify
                pdt_obj.verify(item_check_callable)
                LOGGER.info("PDT validation was successful. Object saved: %s" %
                            pdt_obj)
    else:
        pass  # we ignore any PDT requests that don't have a transaction id
        LOGGER.warn("Ignored request since txn_id parameter is missing.")

    context.update({"failed": failed, "pdt_obj": pdt_obj})
    return render_to_response(template, context, RequestContext(request))
