from voluptuous import Schema, Length, All, Required, REMOVE_EXTRA, Range

schemas = {
    '/games/': {
        'POST': Schema({
            Required('name'): All(str, Length(min=1, max=50)),
            Required('grid'): All(str, Length(min=100, max=100))
            }, extra=REMOVE_EXTRA),

        'PATCH': Schema({
            Required('x'): All(int, Range(min=0, max=9)),
            Required('y'): All(int, Range(min=0, max=9))
        }, extra=REMOVE_EXTRA)
    }
}
