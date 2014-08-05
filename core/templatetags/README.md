# Core template tags and filters

## Dict

### get

Return value of dict if it does exists, else return empty string

Usage:

    {% load dict %}

    {{ d|get:"key" }}

With default value:

    {% load dict %}

    {{ d|get:"key"|default:"value" }}
