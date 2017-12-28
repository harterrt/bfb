import gdoc
import clover

def refresh():
    new_ids = get_new_item_ids()
    map(upload_line_item, new_ids)

def upload_line_item(item_id):
    line_item = clover.format_line_item(clover.get_line_item(item_id))
    gdoc.add_line_item(line_item)

def get_new_item_ids():
    all_ids = clover.get_line_item_ids()

    # Get existing items from sheet and filter to ids
    existing_lis = gdoc.get_line_items_from_sheet()
    existing_ids = map(lambda xx: xx['id'], existing_lis)

    new = filter(lambda xx: xx['line_item_id'] not in existing_ids, all_ids)

    return new
