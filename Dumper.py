from OFS.SimpleItem import SimpleItem
from Globals import HTMLFile, package_home
import os, string

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

addDumperForm = HTMLFile( 'addDumper', _dtmldir )

def addDumper( self, id, fspath=None, REQUEST=None ):
    """
    """
    dumper = Dumper()
    dumper.id = id
    dumper._setFSPath( fspath )
    self._setObject( id, dumper )

    if REQUEST is not None:
        REQUEST[ 'RESPONSE' ].redirect( 'manage_main' )

class Dumper( SimpleItem ):
    """
    """
    meta_type = 'Dumper'

    manage_options = ( { 'label'    : 'Edit'
                       , 'action'   : 'editForm'
                       }
                     , { 'label'    : 'Security'
                       , 'action'   : 'manage_access'
                       }
                     )
    
    __ac__permissions = ( ( 'Use Dumper'
                          , ( 'editForm'
                            , 'edit'
                            , 'dumpToFS'
                            )
                          , ( 'Manager', )
                          )
                        )

    fspath = None

    #
    #   Management interface methods.
    #
    index_html = None

    editForm = HTMLFile( 'editDumper', _dtmldir )

    def edit( self, fspath, REQUEST=None ):
        """
            Update the path to which we will dump our peers.
        """
        self._setFSPath( fspath )

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect( self.absolute_url()
                                        + '/editForm'
                                        + '?manage_tabs_message=Dumper+updated.'
                                        )

    def dumpToFS( self, REQUEST=None ):
        """
            Iterate recursively over our peers, creating simulacra
            of them on the filesystem in 'fspath'
        """
        if REQUEST and REQUEST.form.has_key( 'fspath' ):
            self._setFSPath( REQUEST.form[ 'fspath' ] )

        self._dumpFolder( self.aq_parent )

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect( self.absolute_url()
                                        + '/editForm'
                                        + '?manage_tabs_message=Peers+dumped.'
                                        )
 
    #
    #   Utility methods
    #
    def _setFSPath( self, fspath ):
        #   Canonicalize fspath.
        fspath = os.path.normpath( fspath )
        if not os.path.isabs( fspath ):
            raise "Dumper Error", "Path must be absolute."
        self.fspath = fspath

    def _buildPathString( self, path=None ):
        #   Construct a path string, relative to self.fspath.
        if self.fspath is None:
           raise "Dumper Error", "Path not set."

        if path is None:
            path = self.fspath
        else:
            path = os.path.normpath( os.path.join( self.fspath, path ) )
        
        return path

    def _checkFSPath( self, path=None ):
        #   Ensure that fspath/path exists.
        path = self._buildPathString( path )

        if not os.path.exists( path ):
            os.makedirs( path )
        
        return path

    def _createFile( self, path, filename, mode='w' ):
        #   Create/replace file;  return the file object.
        fullpath = "%s/%s" % ( self._checkFSPath( path ), filename )
        return open( fullpath, mode )
    
    def _dumpObject( self, object, path=None ):
        #   Dump one item, using path as prefix.
        try:
            handler = self._handlers.get( object.meta_type, None )
            if handler is not None:
                handler( self, object, path )
                return 1
        except:
            return -1
        return 0
            

    def _dumpObjects( self, objects, path=None ):
        #   Dump each item, using path as prefix.
        dumped = []
        for object in objects:
            if self._dumpObject( object, path ) > 0:
                id = object.id
                if callable( id ):
                    id = id()
                dumped.append( ( id, object.meta_type ) )
        return dumped


    def _writeProperties( self, obj, file ):
        propIDs = obj.propertyIds()
        propIDs.sort()  # help diff out :)
        for propID in propIDs:
            type = obj.getPropertyType( propID )
            value = obj.getProperty( propID )
            file.write( '%s:%s=%s\n' % ( propID, type, value ) )

    #
    #   Type-specific dumpers
    #
    def _dumpFolder( self, obj, path=None ):
        #   Recurse to dump items in a folder.
        if path is None:
            path = ''
        path = os.path.join( path, obj.id )
        file = self._createFile( path, '.properties' )
        self._writeProperties( obj, file )
        file.close()
        dumped = self._dumpObjects( obj.objectValues(), path )
        dumped.sort() # help diff out :)
        file = self._createFile( path, '.objects' )
        for id, meta in dumped:
            file.write( '%s:%s\n' % ( id, meta ) )
        file.close()

    def _dumpDTML( self, obj, path=None, suffix='dtml' ):
        #   Dump obj (assumed to be a DTML Method/Document) to the
        #   filesystem as a file, appending ".dtml" to the name.
        peer_id = obj.id()
        file = self._createFile( path, '%s.%s' % ( peer_id, suffix ) )
        text = obj.raw
        if text[-1] != '\n':
            text = '%s\n' % text
        file.write( text )
        file.close()

    def _dumpDTMLMethod( self, obj, path=None ):
        self._dumpDTML( obj, path )
        file = self._createFile( path, '%s.properties' % obj.id() )
        file.write( 'title:string=%s\n' % obj.title )
        file.close()

    def _dumpDTMLDocument( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a DTML Document) to the
        #   filesystem as a file, appending ".dtml" to the name.
        self._dumpDTML( obj, path )
        file = self._createFile( path, '%s.properties' % obj.id() )
        self._writeProperties( obj, file )
        file.close()

    def _dumpExternalMethod( self, obj, path=None ):
        #   Dump properties of obj (assumed to be an Externa Method) to the
        #   filesystem as a file, appending ".py" to the name.
        file = self._createFile( path, '%s.properties' % obj.id )
        file.write( 'title:string=%s\n' % obj.title )
        file.write( 'module:string=%s\n' % obj._module )
        file.write( 'function:string=%s\n' % obj._function )
        file.close()

    def _dumpFileOrImage( self, obj, path=None ):
        #   Dump properties of obj (assumed to be an Externa Method) to the
        #   filesystem as a file, appending ".py" to the name.
        file = self._createFile( path, '%s.properties' % obj.id() )
        file.write( 'title:string=%s\n' % obj.title )
        file.write( 'content_type:string=%s\n' % obj.content_type )
        file.write( 'precondition:string=%s\n' % obj.precondition )
        file.close()
        file = self._createFile( path, obj.id(), 'wb' )
        data = obj.data
        if type( data ) == type( '' ):
            file.write( data )
        else:
            while data is not None:
                file.write( data.data )
                data = data.next
        file.close()

    def _dumpPythonMethod( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a Python Method) to the
        #   filesystem as a file, appending ".py" to the name.
        body_lines = string.split( obj._body, '\n' )
        body = string.join( body_lines, '\n    ' )
        text = "def %s(%s)\n\n    %s" % ( obj.id, obj._params, body )
        if text[-1] != '\n':
            text = '%s\n' % text
        file = self._createFile( path, '%s.py' % obj.id )
        file.write( text )
        file.close()
        file = self._createFile( path, '%s.properties' % obj.id )
        file.write( 'title:string=%s\n' % obj.title )
        file.close()

    def _dumpSQLMethod( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a SQL Method) to the
        #   filesystem as a file, appending ".sql" to the name.
        file = self._createFile( path, '%s.sql' % obj.id )
        text = "%s\n\n%s" % ( obj.arguments_src, obj.src )
        if text[-1] != '\n':
            text = '%s\n' % text
        file.write( text )
        file.close()
        file = self._createFile( path, '%s.properties' % obj.id )
        file.write( 'title:string=%s\n' % obj.title )
        file.write( 'connection_id:string=%s\n' % obj.connection_id )
        file.write( 'max_rows_:int=%s\n' % obj.max_rows_ )
        file.write( 'max_cache_:int=%s\n' % obj.max_cache_ )
        file.write( 'cache_time_:int=%s\n' % obj.cache_time_ )
        file.write( 'class_name_:string=%s\n' % obj.class_name_ )
        file.write( 'class_file_:string=%s\n' % obj.class_file_ )
        file.close()

    def _dumpZCatalog( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a ZCatalog) to the
        #   filesystem as a file, appending ".catalog" to the name.
        file = self._createFile( path, '%s.catalog' % obj.id )
        for brain in obj.searchResults():
            file.write( '%s\n' % obj.getpath( brain.data_record_id_ ) )
        file.close()
        file = self._createFile( path, '%s.properties' % obj.id )
        file.write( 'title:string=%s\n' % obj.title )
        file.write( 'vocab_id:string=%s\n' % obj.vocab_id )
        file.write( 'threshold:int=%s\n' % obj.threshold )
        file.close()
        file = self._createFile( path, '%s.indexes' % obj.id )
        for index in obj.index_objects():
            file.write( '%s:%s\n' % ( index.id, index.meta_type ) )
        file.close()
        file = self._createFile( path, '%s.metadata' % obj.id )
        for column in obj.schema():
            file.write( '%s\n' % column )
        file.close()
    
    def _dumpZClass( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a ZClass) to the
        #   filesystem as a directory, including propertysheets and
        #   methods, as well as any nested ZClasses.
        if path is None:
            path = ''
        path = os.path.join( path, obj.id )
        file = self._createFile( path, '.properties' )
        file.write( 'title:string=%s\n' % obj.title )
        file.write( 'metatype:string=%s\n' % obj._zclass_.meta_type )
        file.write( 'bases:tokens=%s\n'
                  % string.join( map( lambda klass: str(klass), obj._zbases )
                               , ','
                               )
                  )
        file.write( 'class_id:int=%s\n' % obj._zclass_.__module__ )
        file.close()

        #   Dump icon
        file = self._createFile( path, '.icon', 'wb' )
        img = obj._zclass_.ziconImage
        data = img.data
        if type( data ) == type( '' ):
            file.write( data )
        else:
            while data is not None:
                file.write( data.data )
                data = data.next
        file.close()

        #   Dump views
        file = self._createFile( path, '.views' )
        for view in obj.propertysheets.views.data():
            file.write( '%s:%s\n' % ( view[ 'label' ], view[ 'action' ] ) )
        file.close()

        #   Dump property sheets.
        sheetpath = os.path.join( path, 'propertysheets' , 'common' )
        sheets = self._dumpObjects( obj.propertysheets.common.objectValues()
                                  , sheetpath )
        sheets.sort() # help diff out :)
        file = self._createFile( sheetpath, '.objects' )
        for id, meta in sheets:
            file.write( '%s:%s\n' % ( id, meta ) )
        file.close()

        #   Dump methods
        methodpath = os.path.join( path, 'propertysheets', 'methods' )
        methods = self._dumpObjects( obj.propertysheets.methods.objectValues()
                                   , methodpath )
        methods.sort() # help diff out :)
        file = self._createFile( methodpath, '.objects' )
        for id, meta in methods:
            file.write( '%s:%s\n' % ( id, meta ) )
        file.close()
    
    def _dumpZClassPropertySheet( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a ZClass) to the
        #   filesystem as a directory, including propertysheets and
        #   methods, as well as any nested ZClasses.
        file = self._createFile( path, '%s' % obj.id )
        self._writeProperties( obj, file )
        file.close()

        file = self._createFile( path, '%s.properties' % obj.id )
        file.write( 'title:string=%s\n' % obj.title )
        file.close()
    
    def _dumpPermission( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a Zope Permission) to the
        #   filesystem as a .properties file.
        file = self._createFile( path, '%s.properties' % obj.id )
        file.write( 'title:string=%s\n' % obj.title )
        file.write( 'name:string=%s\n' % obj.name )
        file.close()

    def _dumpFactory( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a Zope Factory) to the
        #   filesystem as a .properties file.
        file = self._createFile( path, '%s.properties' % obj.id )
        file.write( 'title:string=%s\n' % obj.title )
        file.write( 'object_type:string=%s\n' % obj.object_type )
        file.write( 'initial:string=%s\n' % obj.initial )
        file.write( 'permission:string=%s\n' % obj.permission )
        file.close()

    def _dumpWizard( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a Wizard) to the
        #   filesystem as a directory, containing a .properties file
        #   and analogues for the pages.
        if path is None:
            path = ''
        path = os.path.join( path, obj.id )
        file = self._createFile( path, '.properties' )
        file.write( 'title:string=%s\n' % obj.title )
        file.write( 'description:text=[[%s]]\n' % obj.description )
        file.write( 'wizard_action:string=%s\n' % obj.wizard_action )
        file.write( 'wizard_icon:string=%s\n' % obj.wizard_icon )
        file.write( 'wizard_hide_title:int=%s\n' % obj.wizard_hide_title )
        file.write( 'wizard_stepcount:int=%s\n' % obj.wizard_stepcount )
        file.close()

        pages = self._dumpObjects( obj.objectValues(), path )

        pages.sort() # help diff out :)
        file = self._createFile( path, '.objects' )
        for id, meta in pages:
            file.write( '%s:%s\n' % ( id, meta ) )
        file.close()

    def _dumpWizardPage( self, obj, path=None ):
        #   Dump properties of obj (assumed to be a WizardPage) to the
        #   filesystem as a file, appending ".wizardpage" to the name.
        self._dumpDTML( obj, path, 'wizardpage' )
        file = self._createFile( path, '%s.properties' % obj.id() )
        self._writeProperties( obj, file )
        file.close()

    _handlers = { 'DTML Method'     : _dumpDTMLMethod
                , 'DTML Document'   : _dumpDTMLDocument
                , 'Folder'          : _dumpFolder
                , 'External Method' : _dumpExternalMethod
                , 'File'            : _dumpFileOrImage
                , 'Image'           : _dumpFileOrImage
                , 'Python Method'   : _dumpPythonMethod
                , 'Z SQL Method'    : _dumpSQLMethod
                , 'ZCatalog'        : _dumpZCatalog
                , 'Z Class'         : _dumpZClass
                , 'Common Instance Property Sheet'
                                    : _dumpZClassPropertySheet
                , 'Zope Permission' : _dumpPermission
                , 'Zope Factory'    : _dumpFactory
                , 'Wizard'          : _dumpWizard
                , 'Wizard Page'     : _dumpWizardPage
               #, 'SQL DB Conn'     : _dumpDBConn
                }

    def testDump( self, peer_path, path=None, REQUEST=None ):
        """
            Test dumping a single item.
        """
        obj = self.aq_parent.restrictedTraverse( peer_path )
        self._dumpObject( obj )
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect( self.absolute_url()
                                        + '/editForm'
                                        + '?manage_tabs_message=%s+dumped.'
                                        % peer_path
                                        )
