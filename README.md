# yamodool

YAML models of Odoo

## Installation

Install with:

```bash
pip install -e git+git@gitlab.crnd.pro:crnd/yamodool.git#egg=yamodool
```

or

```bash
pip install -e git+https://gitlab.crnd.pro/crnd/yamodool#egg=yamodool
```


## Usage


1. Add following lines into `__init__.py` file of your addon

    ```python
    from yamodool import load_yamodool
    load_yamodool()
    ```
2. Create subdirectory `yamodools` in your addon.
3. Create model definition in file `yamodools/my_super_model.yml`

    ```yaml
    name: my.super.model
    order: sequence ASC
    fields:
        sequence:
            type: Integer
            default: 5
        active:
            type: Boolean
            default: true
            index: true
        name:
            type: Char
            required: true
            index: true
            translate: true
            help: Record name
        contact_id:
            type: Many2one
            required: true
            comodel_name: res.users
        contact_type:
            type: Selection
            selection:
                - Address
                - Contact
                - Company
    constraints:
        unique_name:
            type: unique
            fields:
                - name
            message: Name must be unique
        ascii_name:
            type: check
            check: 'name ~ ''^[a-zA-Z0-9\-_]*$'''
            message: Name must be ascii only
    ```
4. Add `dependencies` section to addon's manifest file
    ```python
    'external_dependencies': {
        'python': [
            'yamodool',
        ],
    },
    ```

