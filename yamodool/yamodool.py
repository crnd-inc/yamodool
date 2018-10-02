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

    def add_field_counter(self, field_name, field_attrs):
        count_field = field_attrs.pop('count_field')
        compute_fn_name = field_attrs.pop(
            'compute_fn_name',
            '_compute_%s' % field_name)
        self.model_attrs[field_name] = odoo.fields.Integer(
            compute=compute_fn_name, **field_attrs)

        @odoo.api.depends(count_field)
        def compute_method(self):
            for record in self:
                record[field_name] = len(record[count_field])

        self.model_attrs[compute_fn_name] = compute_method

    def add_model_field(self, field_name, field_attrs):
        special = field_attrs.pop('special', None)
        if special and special == 'Counter':
            self.add_field_counter(field_name, field_attrs)
        else:
            field_type = field_attrs.pop('type')
            field_cls = getattr(odoo.fields, field_type)
            self.model_attrs[field_name] = field_cls(**field_attrs)

    def add_fields(self):
        if 'fields' not in self.yml_data:
            return
        for field_name, field_attrs in self.yml_data['fields'].items():
            self.add_model_field(field_name, field_attrs)

    def add_uniq_constraint(self, name, constraint):
        self.model_attrs.setdefault('_sql_constraints', [])
        self.model_attrs['_sql_constraints'].append((
            name,
            'UNIQUE (%s)' % ', '.join(constraint['fields']),
            constraint['message'],
        ))

    def add_check_constraint(self, name, constraint):
        self.model_attrs.setdefault('_sql_constraints', [])
        self.model_attrs['_sql_constraints'].append((
            name,
            'CHECK (%s)' % constraint['check'],
            constraint['message'],
        ))

    def add_constraints(self):
        if 'constraints' not in self.yml_data:
            return
        for name, constraint in self.yml_data['constraints'].items():
            if constraint['type'] == 'unique':
                self.add_uniq_constraint(name, constraint)
            elif constraint['type'] == 'check':
                self.add_check_constraint(name, constraint)
            else:
                raise YAModoolError(
                    "Unsupported constraint type %s" % constraint['type'])

    def add_name_attr(self):
        self.add_optional_attr('_name', 'name')
        if not self.model_attrs.get('_name'):
            name = os.path.splitext(os.path.basename(self.file_path))[0]
            self.model_attrs['_name'] = name.lower().replace('_', '.')

    def parse_yml_data(self):
        _logger.info("Parsing yamodool data: %r", self.file_path)
        self.add_name_attr()
        self.add_optional_attr('_order', 'order')
        self.add_optional_attr('_description', 'description')
        self.add_optional_attr('_inherit', 'inherit')
        self.add_fields()
        self.add_constraints()
        _logger.info("yamodool data parsed: %r", self.file_path)

    def get_model_class(self):
        model_type = self.yml_data.get('type', 'model')
        if model_type == 'model':
            return odoo.models.Model
        elif model_type == 'transient':
            return odoo.models.TransientModel
        elif model_type == 'abstract':
            return odoo.models.AbstractModel
        raise YAModoolError(
            "Unknown model type. "
            "Possible values: model, abstract, transient.")

    def generate_model(self, module):
        _logger.info("Generating model for yamodool data: %r", self.file_path)
        try:
            self.parse_yml_data()
        except Exception as exc:
            _logger.error(
                "Cannot parse yamodool data: %s",
                self.file_path, exc_info=True)
            raise YAModoolError(str(exc))

        # Update model's module. This is required to register model in registry
        self.model_attrs['__module__'] = module

        YAModoolModel = type(
            'yamodool',
            (self.get_model_class(),),
            self.model_attrs
        )

        _logger.info(
            "Created model class:\n\tname=%s\n\tinherit=%s",
            getattr(YAModoolModel, '_name', None),
            getattr(YAModoolModel, '_inherit', None))
        return YAModoolModel


def load_yamodool(path=None):
    """ Load YAModool model.

        - If path is not specified, yamodool will try to
          guess it based on calling context
        - If path points to file, then that file will be parsed
        - if path points to directory, then yamodool will look for .yml files
          in that directory and try to build model for each file.
          All files in that directory must be valid yamodool models.
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
