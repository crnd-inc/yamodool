import os
import os.path
import inspect

import odoo

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import logging
_logger = logging.getLogger(__name__)


class YAModoolError(Exception):
    pass


class YAModool(object):
    def __init__(self, file_path):
        self.file_path = file_path
        with open(file_path, 'rt') as f:
            self.yml_data = load(f, Loader=Loader)

        self.model_attrs = {}

    def add_optional_attr(self, dst_attr, src_attr):
        if src_attr in self.yml_data:
            self.model_attrs[dst_attr] = self.yml_data[src_attr]

    def add_model_field(self, field_name, field_attrs):
        field_cls = getattr(odoo.fields, field_attrs.pop('type'))
        self.model_attrs[field_name] = field_cls(**field_attrs)

    def add_fields(self):
        if 'fields' not in self.yml_data:
            return
        for field_name, field_attrs in self.yml_data['fields'].items():
            self.add_model_field(field_name, field_attrs)

    def parse_yml_data(self):
        _logger.info("Parsing yamodool data: %r", self.file_path)
        self.add_optional_attr('_name', 'name')
        self.add_optional_attr('_order', 'order')
        self.add_fields()
        _logger.info("yamodool data parsed: %r", self.file_path)

    def generate_model(self, module):
        _logger.info("Generating model for yamodool data: %r", self.file_path)
        try:
            self.parse_yml_data()
        except Exception as exc:
            _logger.error(
                "Cannot parse yamodool data: %s",
                self.file_path, exc_info=True)
            raise YAModoolError(str(exc))

        # Update model's module
        self.model_attrs['__module__'] = module

        # Create mixin class that contain all required attribute.
        # Here we use mixin, because when model class created via *type* it
        # will not be registered in registry.
        # TODO: investigate why
        # mixin_cls = type('YAModool', (object,), self.model_attrs)
        YAModoolModel = type(
            'yamodool',
            (odoo.models.Model,),
            self.model_attrs
        )

        _logger.info(
            "Created model class:\n\tname=%s\n\tinherit=%s",
            getattr(YAModoolModel, '_name', None),
            getattr(YAModoolModel, '_inherit', None))
        return YAModoolModel


def load_yamodool(path=None):
    """ Load YAModool model by file path
    """
    # Guess module name
    module = inspect.stack()[1][0].f_locals['__name__']
    if not module.startswith('odoo.addons'):
        raise YAModoolError(
            "Cannot determine model module. perhaps *load_yamodool* called "
            "not from odoo addon"
        )

    # Look for models in yamodools direcotry of addon if path is None
    if path is None:
        path = inspect.stack()[1][0].f_locals['__path__']
        if path and os.path.exists(os.path.join(path[0], 'yamodools')):
            path = os.path.join(path[0], 'yamodools')

    if path is None:
        return

    # Create models
    if os.path.isfile(path):
        YAModool(path).generate_model(module)
    elif os.path.isdir(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                if filename.endswith('.yml'):
                    YAModool(os.path.join(dirpath, filename)).generate_model(
                        module)
    else:
        raise YAModoolError("Cannot load yamodools from path: %s" % path)
