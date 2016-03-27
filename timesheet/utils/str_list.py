def str_list(*items, quote=False, delimitor=',', conjunction='&'):
    quote       = "'" if quote else ''
    delimitor   = "{} ".format(delimitor)
    conjunction = " {} ".format(conjunction)
    items       = ["'{}'".format(i) for i in items] if quote else list(items)

    try:
        final_item = items.pop(-1)
    except IndexError:
        return ''
    else:
        leading_items = delimitor.join(items)
        both_items    = (leading_items, final_item)
        return conjunction.join(both_items) if leading_items else final_item
