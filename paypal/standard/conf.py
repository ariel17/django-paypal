from django.conf import settings

class PayPalSettingsError(Exception):
    """Raised when settings be bad."""
    

TEST = getattr(settings, "PAYPAL_TEST", True)


RECEIVER_EMAIL = settings.PAYPAL_RECEIVER_EMAIL


# API Endpoints.
POSTBACK_ENDPOINT = "https://www.paypal.com/cgi-bin/webscr"
SANDBOX_POSTBACK_ENDPOINT = "https://www.sandbox.paypal.com/cgi-bin/webscr"

# Images
IMAGE = getattr(settings, "PAYPAL_IMAGE", "http://images.paypal.com/images/x-click-but01.gif")
SUBSCRIPTION_IMAGE = getattr(settings, "PAYPAL_SUBSCRIPTION_IMAGE", "https://www.paypal.com/en_US/i/btn/btn_subscribeCC_LG.gif")
DONATION_IMAGE = getattr(settings, "PAYPAL_DONATION_IMAGE", "https://www.paypal.com/en_US/i/btn/btn_donateCC_LG.gif")
SANDBOX_IMAGE = getattr(settings, "PAYPAL_SANDBOX_IMAGE", "https://www.sandbox.paypal.com/en_US/i/btn/btn_buynowCC_LG.gif")
SUBSCRIPTION_SANDBOX_IMAGE = getattr(settings, "PAYPAL_SUBSCRIPTION_SANDBOX_IMAGE", "https://www.sandbox.paypal.com/en_US/i/btn/btn_subscribeCC_LG.gif")
DONATION_SANDBOX_IMAGE = getattr(settings, "PAYPAL_DONATION_SANDBOX_IMAGE", "https://www.sandbox.paypal.com/en_US/i/btn/btn_donateCC_LG.gif")

# "payment_status" request paremeter values
# Source: https://developer.paypal.com/webapps/developer/docs/classic/ipn/integration-guide/IPNandPDTVariables/
PAYMENT_STATUS_CANCELED_REVERSAL = "Canceled_Reversal"
PAYMENT_STATUS_COMPLETED = "Completed"
PAYMENT_STATUS_CREATED = "Created"
PAYMENT_STATUS_DENIED = "Denied"
PAYMENT_STATUS_EXPIRED = "Expired"
PAYMENT_STATUS_FAILED = "Failed"
PAYMENT_STATUS_PENDING = "Pending"
PAYMENT_STATUS_REFUNDED = "Refunded"
PAYMENT_STATUS_REVERSED = "Reversed"
PAYMENT_STATUS_PROCESSED = "Processed"
PAYMENT_STATUS_VOIDED = "Voided"
