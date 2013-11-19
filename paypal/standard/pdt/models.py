#!/usr/bin/env python
# -*- coding: utf-8 -*-


from urllib import unquote_plus
import urllib2
import logging

from django.db import models
from django.conf import settings
from django.utils.http import urlencode

from paypal.standard.models import PayPalStandardBase
from paypal.standard.conf import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT
from paypal.standard.pdt.signals import pdt_successful, pdt_failed


LOGGER = logging.getLogger(__name__)


# ### Todo: Move this logic to conf.py:
# if paypal.standard.pdt is in installed apps
# ... then check for this setting in conf.py
class PayPalSettingsError(Exception):
    """Raised when settings are incorrect."""


try:
    IDENTITY_TOKEN = settings.PAYPAL_IDENTITY_TOKEN
except:
    raise PayPalSettingsError("You must set PAYPAL_IDENTITY_TOKEN in "
                              "settings.py. Get this token by enabling PDT "
                              "in your PayPal account.")


class PayPalPDT(PayPalStandardBase):
    format = u"<PDT: %s %s>"

    amt = models.DecimalField(max_digits=64, decimal_places=2, default=0,
                              blank=True, null=True)
    cm = models.CharField(max_length=255, blank=True)
    sig = models.CharField(max_length=255, blank=True)
    tx = models.CharField(max_length=255, blank=True)
    st = models.CharField(max_length=32, blank=True)

    class Meta:
        db_table = "paypal_pdt"
        verbose_name = "PayPal PDT"

    def _postback(self):
        """
        Perform PayPal PDT Postback validation.
        Sends the transaction ID and business token to PayPal which responses
        with SUCCESS or FAILED.
        """
        postback_dict = dict(cmd="_notify-synch", at=IDENTITY_TOKEN,
                             tx=self.txn_id)
        LOGGER.debug("Postback: URL=%s, parameters=%s" % (self.get_endpoint(),
                     postback_dict))

        postback_params = urlencode(postback_dict)
        return urllib2.urlopen(self.get_endpoint(), postback_params).read().\
            encode(settings.DEFAULT_CHARSET)

    def get_endpoint(self):
        """
        Use the sandbox when in DEBUG mode as we don't have a test_ipn variable
        in pdt.
        """
        if getattr(settings, 'PAYPAL_DEBUG', settings.DEBUG):
            return SANDBOX_POSTBACK_ENDPOINT
        else:
            return POSTBACK_ENDPOINT

    def _verify_postback(self):
        """
        Process the postback response for PDT notifications.
        """
        # Now we don't really care what result was, just whether a flag was
        # set or not.
        result = False

        response_list = self.response.split('\n')
        for i, line in enumerate(response_list):
            unquoted_line = unquote_plus(line).strip()
            if i == 0:
                self.st = unquoted_line
                if self.st == "SUCCESS":
                    result = True
                    LOGGER.info("Paypal's postback validation was succesful.")
            else:
                if self.st != "SUCCESS":
                    self.set_flag(line)
                    LOGGER.error("Paypal's postback validation has errors: "
                                 "%s" % self.response)
                    break

                try:
                    if not unquoted_line.startswith(' -'):
                        k, v = unquoted_line.split('=')
                        setattr(self, k.strip(), v.strip())
                except ValueError:
                    pass

        self.save()
        return result

    def send_signals(self):
        # Send the PDT signals...
        if self.flag:
            pdt_failed.send(sender=self)
        else:
            pdt_successful.send(sender=self)
