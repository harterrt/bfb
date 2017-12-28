from datetime import datetime as dt
from pytz import timezone
import itertools
import requests
import json

with open('../auth/token.txt') as oo:
    token = oo.next().strip()

def get_line_items(line_item_ids):
    return map(get_line_item, line_item_ids)

def format_line_items(line_items):
    return map(format_line_item, line_items)

def format_line_item(line_item):
    return stringify_line_item(parse_line_item(clean_line_item(line_item)))

def clean_line_item(line_item):
    keep_keys = ['exchanged', 'id', 'name', 'price',
                 'refunded']
    out = {key: line_item[key] for key in line_item.keys()
           if key in keep_keys}

    # For some reason gdoc doesn't accept camel case titles
    out['created'] = line_item['createdTime']

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
    created = dt.fromtimestamp(int(line_item['created'])/1000)
    eastern_created = et_tz.localize(created)
    out['created'] = eastern_created.strftime('%Y-%m-%d %H:%M')
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

def get_line_item(line_item_id):
    api_fmt = "https://api.clover.com/v3/merchants/MERCHANTID/orders/{order_id}/line_items/{line_item_id}?expand=modifications&access_token={token}"
    api_call = api_fmt.format(order_id=line_item_id['order_id'],
                              line_item_id=line_item_id['line_item_id'],
                              token=token)

    response = requests.get(api_call)
    return(json.loads(response.text))

def get_line_item_ids(orders=None):
    if not orders:
        orders = get_all_orders()

    # Remove open orders. No line item elements
    closed_orders = filter(lambda xx: xx['state'] == u'locked', orders)

    order_list_items = map(filter_line_item_ids, closed_orders)

    # Combine the lists of item ids from each order
    return list(itertools.chain(*order_list_items))

def filter_line_item_ids(order):
    items = order['lineItems']['elements']
    return map(lambda xx: {'line_item_id':xx['id'],
                           'order_id':xx['orderRef']['id']},
               items)

def get_all_orders():
    recent_response = get_orders(limit = 1000)
    out = recent_response
    index = 1

    while len(recent_response) == 1000:
        recent_response = get_orders(limit = 1000, offset = index*1000)
        out = out + recent_response
        # Implement this! Limits load on clover API, fixes OOM issue.
        # earliest = min(map(lambda xx: xx['createdTime'], out))
        index = index + 1
    
    return out

def get_orders(limit=100, offset=0):
    api_fmt = ("https://api.clover.com/v3/merchants/MERCHANTID/orders/"
               "?offset={offset}&limit={limit}&expand=lineItems"
               "&access_token={token}")
    api_call = api_fmt.format(token=token, limit=limit, offset=offset)
    response = requests.get(api_call)
    return(json.loads(response.text)['elements'])

# Utilities
def pprint(obj):
    print json.dumps(obj, sort_keys=True, indent=4)
