# Core template tags and filters

## Dict

### get

Return value of dict if it does exists, else return empty string

Usage:

    {{ dict|get:"key" }}

With default value:

    {{ dict|get:"key"|default:"value" }}
