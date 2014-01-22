
"""
Amazon Web Services API

Rationale: the standard boto library throws errors on GAE, seemingly due to
google.appengine.api.urlfetch
"""

import logging
from time import mktime
import datetime
from wsgiref.handlers import format_date_time
import hmac
import hashlib
import base64

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from urllib import urlencode

from google.appengine.api import urlfetch


def rfc_1123_timestamp(dt):
    stamp = mktime(dt.timetuple())
    return format_date_time(stamp)


def iso_8601_timestamp(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def aws_api_base_url(region_name):
    return u"https://email.%s.amazonaws.com" % region_name


def post_signed(url, params, aws_access_key_id, aws_secret_access_key):
    if isinstance(aws_access_key_id, unicode):
        aws_access_key_id = aws_access_key_id.encode('ascii')
    if isinstance(aws_secret_access_key, unicode):
        aws_secret_access_key = aws_secret_access_key.encode('ascii')
    now = datetime.datetime.utcnow()
    rfc_timestamp = rfc_1123_timestamp(now)
    iso_timestamp = iso_8601_timestamp(now)
    hmac_hash = hmac.new(aws_secret_access_key, rfc_timestamp, hashlib.sha1)
    encoded_hash = base64.b64encode(hmac_hash.digest())
    x_amzn_auth = (
        "AWS3-HTTPS " +
        "AWSAccessKeyId=%s, " % aws_access_key_id +
        "Algorithm=HmacSHA1, " +
        "Signature=%s" % encoded_hash
    )
    payload = dict({
            "AWSAccessKeyId": aws_access_key_id,
            "Timestamp": iso_timestamp, 
        },
        **params
    )
    response = urlfetch.fetch(
        url=url,
        method="POST",
        headers={
            "Date": rfc_timestamp,
            "X-Amzn-Authorization": x_amzn_auth,
        },
        payload=urlencode(payload),
    )
    if "Error" in response.content:
        logging.error("AWS ERROR: %s" % response.content)
    return response


def ses_send_email(
        source, to_addresses, subject, body, cc=None, bcc=None, html_body=None,
        aws_region=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
    ):
    # construct multipart email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = source
    msg['To'] = u', '.join(to_addresses)

    text_part = MIMEText(body, 'plain')
    msg.attach(text_part)
    if html_body:
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

    # post to AWS SES
    url = aws_api_base_url(aws_region)
    post_signed(
        url,
        params={
            'Action': 'SendRawEmail',
            'RawMessage.Data': base64.b64encode(msg.as_string()),
        },
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
