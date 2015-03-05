``plone2.0_export.py``
======================

Export data from an old plone site.

Installation
------------

* Create an external method in your plone site.

   - Copy collective.jsonmigrator/export_scripts/plone2.0_export.pt in *INSTANCE/Extensions* directory
   - Connect to ZMI
   - Add an External Method, and fill out the form with ::

      id = your_id
      module name = plone_2.0export
      method = export_plone20

* Create an jsonmigrator.ini in order to configure export process.


Syntax of configuration
-----------------------


Options
+++++++

 * In DEFAULT section

   - HOMEDIR => where we create json file. This directory must exists !! Each time that export process is invoked, an new folder is created . In each folder created , every 1000 objects created, script create an new folder. The directory struture look like that::

      HOMEDIR
       |_ <id_object>_<date_export>
           |_ 0
              |_ 1.json
              |_ 2.json
              |_ ...
              |_ 999.json
           |_ 1
              |_ 1000.json
              |_ 1001.json
              |_ ...
              |_ 1999.json
           ....

     You can have also file name loke xxx.json-file-x . This is binary file of exported content.

   - CLASSNAME_TO_SKIP_LAUD => This is a list of classname. Object of this classname where are skip by the export process

   - CLASSNAME_TO_SKIP => This is a list of classname. Object of this classname where are skip by the export process

   - ID_TO_SKIP => This is a list of id object . Object wich id is equal to an member of this list is skipping of the process.

   - NON_FOLDERISH_CLASSNAME => This is a list of classname.  Object of this classname are considered as non folderish content.

   - JUST_TREAT_WAPPER => If true CLASSNAME_TO_SKIP_LAUD and CLASSNAME_TO_SKIP have no effect. Just object that are mapping in CLASSNAME_TO_WAPPER_MAP are treated

   - MAX_CACHE_DB => a int number that indicate when the process purge the zodb cache (avoid memory error)

 * In CLASSNAME_TO_WAPPER_MAP

  - ClassName=Wrapper => you configure the export wrapper use for object of ClassName


Example
+++++++

::

 [DEFAULT]
 HOMEDIR=c:\dt\plone2.1\export
 JUST_TREAT_WAPPER=True
 NON_FOLDERISH_CLASSNAME=DPLDTArticle
        DPLDTIssue
        DPLDTPerformance
        DPLDTTraining
 MAX_CACHE_DB=250

 [CLASSNAME_TO_WAPPER_MAP]
 LargePloneFolder=BaseWrapper
 Folder=BaseWrapper
 PloneSite=BaseWrapper
 PloneFolder=BaseWrapper
 Document=DocumentWrapper
 File=FileWrapper
 YourSpecificContentType=ArchetypesWrapper


Existing Wrapper
++++++++++++++++

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: BaseWrapper
    :end-before: def


 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: DocumentWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: I18NFolderWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: LinkWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: NewsItemWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: ListCriteriaWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: StringCriteriaWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: SortCriteriaWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: DateCriteriaWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: FileWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: ImageWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: EventWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: ArchetypesWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: I18NLayerWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: Article322Wrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: ArticleWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: ZPhotoWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: ZPhotoSlidesWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: ContentPanels
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: LocalFSWrapper
    :end-before: def

 .. literalinclude:: ../export_scripts/plone2.0_export.py
    :pyobject: ZopeObjectWrapper
    :end-before: def





