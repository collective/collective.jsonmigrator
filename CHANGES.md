## Changelog

3.0.2 (unreleased)
------------------

- Add Python 3.10 and 3.11 support @wesleybl

- Remove ``z3c.autoinclude`` of entry_points @wesleybl


3.0.1 (2022-08-18)
------------------

- Fix README rendering on pypi @ericof


3.0.0 (2022-08-18)

- Implement plone/code-analysis-action @ericof

- Add support to Plone 6.0 @ericof

- Drop support to Plone versions 4.3, 5.0 and 5.1 @ericof

- Drop support to Python 2.7 @ericof


### 2.0.0 (2021-09-22)

- Add blueprint to import translations from plone.app.multilingual. @wesleybl

- Don't encode property value in Python 3. @wesleybl

- Allows use of blueprint collective.jsonmigrator.owner in dexterity objects. @wesleybl

- Don't encode path in Python 3. @wesleybl

- Explicitly depends on six. @wesleybl

- Don't use simplejson. @wesleybl

- Add support to Plone 5.1 and Plone 5.2. @wesleybl

- No longer depend on zope.app.container.notifyContainerModified.
  Use from zope.container.contained import notifyContainerModified instead. @mathias.leimgruber

- Python 3 compatibility @ksuess


### 1.0.1 (2018-06-11)

- if certain properties (default page, others?) are unicode they cause site failures. @sunew


### 1.0 (2017-12-22)

- Set default value of config field for jsonmigrator-run view. @bsuttor

- Fix workflow_history to also work with dexterity @erral, @djowett


### 0.4 (2016-05-24)

- Do not require simplejson if we already have the native json module. @ale-rt


### 0.3 (2015-10-25)

- Move pipeline configurations into own directory pipelines. @thet

- Restructure blueprints to be in blueprints directory and integrate orphaned
  blueprints from collective.blueprint.jsonmigrator. @thet

- PEP 8. @thet, @mauritsvanrees

- Log json decode error instead of crashing @marciomazza
