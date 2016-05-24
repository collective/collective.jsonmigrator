Changelog
=========

0.4 (2016-05-24)
----------------

- Do not require simplejson if we already have the native json module.
  [ale-rt]


0.3 (2015-10-25)
----------------

- Move pipeline configurations into own directory pipelines.
  [thet]

- Restructure blueprints to be in blueprints directory and integrate orphaned
  blueprints from collective.blueprint.jsonmigrator.
  [thet]

- PEP 8.
  [thet, mauritsvanrees]

- Log json decode error instead of crashing [marciomazza]
