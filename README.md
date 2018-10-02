# yamodool

YAML models of Odoo

## WARNING

Current project stage is *Proof of Concept*:
- no tests,
- no stability,
- everything may change next minute

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
    description: My super model
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

## Examples

There is *examples* firectory in project root, that contains example models.
Look there for more features.


## Goals

The main goal of this project is to separate model definition from python code
in a way that will not conflict with Odoo.
