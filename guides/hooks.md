# Hook examples

This interface represents all script hooks that can be registered to customize the order logic. It contains the extension points (hook names), and the functions that are called by each extension point. A function must be defined inside a JavaScript source and must be exported. The script with the exported hook function must be located inside a site cartridge. Inside the site cartridge a 'package.json' file with a 'hooks' entry must exist.

```json
"hooks": "./hooks.json"
```

The hooks entry links to a json file, relative to the 'package.json' file. This file lists all registered hooks inside the hooks property:

```json
"hooks": [
     {"name": "dw.order.createOrderNo", "script": "./orders.ds"},
]
```

A hook entry has a 'name' and a 'script' property.

* The 'name' contains the extension point, the hook name.
* The 'script' contains the script relative to the hooks file, with the exported hook function.
