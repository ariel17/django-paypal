#!/usr/bin/env python
# -*- coding: utf-8 -*-


from urllib import unquote_plus
import urllib2
import logging

from django.conf import settings
from django.db import models
from django.http import QueryDict
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
        # from paypal.standard.pdt.forms import PayPalPDTForm

        # Now we don't really care what result was, just whether a flag was
        # set or not.
        result = False
        response_dict = {}

        response_list = self.response.split('\n')
        for i, line in enumerate(response_list):
            unquoted_line = unquote_plus(line).strip()
            if i == 0:
                self.st = unquoted_line
                if self.st == "SUCCESS":
                    result = True
                    self.set_flag(line)
                    LOGGER.info("Paypal's postback validation was succesful.")
            else:
                if self.st != "SUCCESS":
                    LOGGER.error("Paypal's postback validation has errors: "
                                 "%s" % self.response)
                    break

                try:
                    if not unquoted_line.startswith(' -'):
                        k, v = unquoted_line.split('=')
                        response_dict[k.strip()] = v.strip()
                        setattr(self, k.strip(), v.strip())

                except ValueError:
                    pass

        if not self.item_number:
            self.item_number = 0

        if not self.payment_gross:
            self.payment_gross = 0

        if not self.payment_fee:
            self.payment_fee = 0

        # Decoding all unicode to utf-8
        self.payer_business_name = self.payer_business_name.decode(
            "utf-8", "ignore")
        self.first_name = self.first_name.decode("utf-8", "ignore")
        self.last_name = self.last_name.decode("utf-8", "ignore")

        # Saving current information
        try:
            self.save()

        except:
            self.payment_date = None
            self.save()

        # Updating object with response data, using form validations
        # qd = QueryDict("", mutable=True)
        # qd.update(response_dict)
        # qd.update(dict(ipaddress=self.ipaddress, st=self.st,
        #           flag_info=self.flag_info))

        # pdt_form = PayPalPDTForm(qd, instance=self)
        # pdt_form.save()

        return result

    def send_signals(self):
        # Send the PDT signals...
        if self.flag:
            LOGGER.info("Sending signals: pdt_failed")
            pdt_failed.send(sender=self)
        else:
            LOGGER.info("Sending signals: pdt_successful")
            pdt_successful.send(sender=self)
