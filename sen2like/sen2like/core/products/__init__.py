import csv
import inspect
import logging
import os
import sys
from collections import OrderedDict

from core.module_loader import dynamic_loader, get_proj_dir

log = logging.getLogger('Sen2Like')

PRODUCTS = {}
BANDS_MAPPING = {}


def is_product(item):
    """Determines if `item` is a `product.S2L_Product`."""
    from core.products.product import S2L_Product
    return inspect.isclass(item) and issubclass(item, S2L_Product) and item.__name__ != S2L_Product.__name__


def get_product_from_sensor_name(sensor):
    """Get product corresponding to given sensor name.

    :param sensor: Product sensor name
    :return:
    """
    for current_product in PRODUCTS.values():
        if getattr(current_product, 'is_final', False) and sensor in getattr(current_product, 'supported_sensors', []):
            return current_product


def get_product(product_path):
    """Get product corresponding to given product.

    :param product_path: Path of the product file to read
    :return:
    """
    products = [_product for _product in PRODUCTS.values() if _product.can_handle(product_path)]
    if len(products) == 1:
        return products[0]
    if len(products) > 1:
        log.error('Multiple products reader compatible with %s' % product_path)
    else:
        log.error("No product reader compatible with %s" % product_path)


def read_mapping(product_class):
    """Read bands mapping file for the given class."""
    directory = os.path.dirname(inspect.getfile(product_class))
    filename = os.path.join(directory, 'bands.csv')
    if not os.path.exists(filename):
        log.error("Invalid mapping filename: %s" % filename)
        return {}
    with open(filename, 'rt') as fp:
        csv_reader = csv.reader(fp)
        next(csv_reader)
        mapping = OrderedDict({m[0]: m[1] for m in csv_reader})
    return mapping


# Loads products
for product in dynamic_loader(get_proj_dir(__file__), 'products', is_product):
    PRODUCTS[product.__name__] = product
    setattr(sys.modules[__name__], product.__name__, product)
