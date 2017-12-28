import time
from pytz import timezone
import string
import json
from datetime import timedelta, datetime
import requests
from functional import seq

def _join(this, that):
    out = this.copy()
    out.update(that)

    return out

def _to_epoch(date):
    """Converts python datetime to clover epoch"""
    return(int(date.strftime('%s')) * 1000)

class Clover(object):
    url_fmt = ("https://api.clover.com/v3/merchants/{merchant_id}/{endpoint}/"
               "?access_token={access_token}")

    def __init__(self, merchant_id, access_token):
        self.url_parameters = {
            'merchant_id': merchant_id,
            'access_token': access_token,
        }
        self.attempts = 0

    @classmethod
    def from_config(cls, config):
        return cls(
            config.contents['merchant_id'],
            config.contents['access_token']
        )

    def get_all_orders(self, day):
        limit = 1000

        def get_orders(offset):
            url = (self.url_fmt + "&" + "&".join([
                'offset=' + str(offset), 'limit=' + str(limit),
                'expand=lineItems',
                'filter=createdTime>=' + str(_to_epoch(day)),
                'filter=createdTime<' + str(_to_epoch(day + timedelta(1))),
            ])).format(**_join(self.url_parameters, {'endpoint': 'orders'}))

            response = requests.get(url)
            return(json.loads(response.text)['elements'])

        recent_response = get_orders(0)
        out = recent_response
        index = 1

        while len(recent_response) == limit:
            recent_response = get_orders(
                offset = index * limit
            )
            out = out + recent_response
            index = index + 1
        
        return out

    def get_line_item_ids(self, day):
        orders = seq(self.get_all_orders(day))

        return (
            orders
            # Filter to closed orders since open orders can have no line items
            .filter(lambda x: x['state'] == u'locked')
            # Convert to lists of (line item id, order id) pairs
            .flat_map(lambda x: x['lineItems']['elements'])
            .map(lambda x: {
                'line_item_id': x['id'],
                'order_id': x['orderRef']['id']
            })
        )

    def get_all_line_items(self, day):
        return (
            seq(self.get_line_item_ids(day))
            .map(self.get_line_item)
            .map(clean_line_item)
            .map(parse_line_item)
            .map(stringify_line_item)
        )

    def get_line_item(self, line_item_id):
        url = (
            (self.url_fmt + '&expand=modifications')
            .format(**_join(
                self.url_parameters,
                {'endpoint': 'orders/{order_id}/line_items/{line_item_id}'}
            ))
            .format(**line_item_id)
        )

        # Poll clover with exponential backoff
        no_response = True
        while self.attempts <= 10 and no_response:
            time.sleep(0.05 * (2 ** self.attempts - 1))
            response = requests.get(url)

            if response.status_code == 429:
                self.attempts += 1
                print("Increased polling break coeff to " + str(self.attempts))
            else:
                no_response = False

        return(json.loads(response.text))

def clean_line_item(line_item):
    keep_keys = ['exchanged', 'id', 'name', 'price', 'refunded', 'createdTime']

    out = {key: line_item[key] for key in line_item.keys() if key in keep_keys}

    # Add an order reference for context
    out['order'] = line_item['orderRef']['id']

    # Summarize the modifications
    if 'modifications' in line_item:
        mods = line_item['modifications']['elements']
    else:
        mods = []

    out[u'modifications'] = len(mods)

    # If price is 0, look to the modifications for more information:
    if (line_item['price'] == 0) & (len(mods) == 1):
        out['price'] = mods[0]['amount']
        out['volume'] = mods[0]['name']
    else:
        out['volume'] = "Unspecified"

    return out

def parse_line_item(line_item):
    out = line_item

    # Parse the creation time
    et_tz = timezone('US/Eastern')
    created = datetime.fromtimestamp(int(line_item['createdTime'])/1000)
    eastern_created = et_tz.localize(created)
    out['createdTime'] = eastern_created.strftime('%Y-%m-%d %H:%M')
    out['year'] = eastern_created.year
    out['month'] = eastern_created.month
    out['day'] = eastern_created.day

    # Adjust price to be dollars
    out['price'] = '${price:.2f}'.format(price=float(line_item['price'])/100)

    return out

def stringify_line_item(line_item):
    # Fix unicode encoding
    def encode_to_string(something):
        if isinstance(something, unicode):
            return str(something.encode('utf8'))
        else:
            return str(something)

    # Map everything to string and return
    return {str(xx): encode_to_string(line_item[xx]) for xx in line_item}


