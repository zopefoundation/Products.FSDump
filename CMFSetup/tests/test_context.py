""" Unit tests for import / export contexts.

$Id$
"""

import unittest
import os
import time
from StringIO import StringIO

from Acquisition import aq_parent
from DateTime.DateTime import DateTime
from OFS.Folder import Folder
from OFS.Image import File

from Products.CMFCore.tests.base.testcase import SecurityRequestTest

from common import FilesystemTestBase
from common import TarballTester
from common import _makeTestFile
from conformance import ConformsToISetupContext
from conformance import ConformsToIImportContext
from conformance import ConformsToIExportContext


class DummySite( Folder ):

    pass

class DummyTool( Folder ):

    pass

class DirectoryImportContextTests( FilesystemTestBase
                                 , ConformsToISetupContext
                                 , ConformsToIImportContext
                                 ):

    _PROFILE_PATH = '/tmp/ICTTexts'

    def _getTargetClass( self ):

        from Products.CMFSetup.context import DirectoryImportContext
        return DirectoryImportContext

    def test_readDataFile_nonesuch( self ):

        FILENAME = 'nonesuch.txt'

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.readDataFile( FILENAME ), None )

    def test_readDataFile_simple( self ):

        from string import printable

        FILENAME = 'simple.txt'
        self._makeFile( FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.readDataFile( FILENAME ), printable )

    def test_readDataFile_subdir( self ):

        from string import printable

        FILENAME = 'subdir/nested.txt'
        self._makeFile( FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.readDataFile( FILENAME ), printable )

    def test_getLastModified_nonesuch( self ):

        FILENAME = 'nonesuch.txt'

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.getLastModified( FILENAME ), None )

    def test_getLastModified_simple( self ):

        from string import printable

        FILENAME = 'simple.txt'
        fqpath = self._makeFile( FILENAME, printable )
        timestamp = os.path.getmtime( fqpath )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.getLastModified( FILENAME ), timestamp )

    def test_getLastModified_subdir( self ):

        from string import printable

        SUBDIR = 'subdir'
        FILENAME = os.path.join( SUBDIR, 'nested.txt' )
        fqpath = self._makeFile( FILENAME, printable )
        timestamp = os.path.getmtime( fqpath )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.getLastModified( FILENAME ), timestamp )

    def test_getLastModified_directory( self ):

        from string import printable

        SUBDIR = 'subdir'
        FILENAME = os.path.join( SUBDIR, 'nested.txt' )
        fqpath = self._makeFile( FILENAME, printable )
        path, file = os.path.split( fqpath )
        timestamp = os.path.getmtime( path )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.getLastModified( SUBDIR ), timestamp )

    def test_isDirectory_nonesuch( self ):

        FILENAME = 'nonesuch.txt'

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.isDirectory( FILENAME ), None )

    def test_isDirectory_simple( self ):

        from string import printable

        FILENAME = 'simple.txt'
        fqpath = self._makeFile( FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.isDirectory( FILENAME ), False )

    def test_isDirectory_nested( self ):

        from string import printable

        SUBDIR = 'subdir'
        FILENAME = os.path.join( SUBDIR, 'nested.txt' )
        fqpath = self._makeFile( FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.isDirectory( FILENAME ), False )

    def test_isDirectory_directory( self ):

        from string import printable

        SUBDIR = 'subdir'
        FILENAME = os.path.join( SUBDIR, 'nested.txt' )
        fqpath = self._makeFile( FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.isDirectory( SUBDIR ), True )

    def test_listDirectory_nonesuch( self ):

        FILENAME = 'nonesuch.txt'

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.listDirectory( FILENAME ), None )

    def test_listDirectory_root( self ):

        from string import printable

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        FILENAME = 'simple.txt'
        self._makeFile( FILENAME, printable )

        self.assertEqual( len( ctx.listDirectory( None ) ), 1 )
        self.failUnless( FILENAME in ctx.listDirectory( None ) )

    def test_listDirectory_simple( self ):

        from string import printable

        FILENAME = 'simple.txt'
        self._makeFile( FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.listDirectory( FILENAME ), None )

    def test_listDirectory_nested( self ):

        from string import printable

        SUBDIR = 'subdir'
        FILENAME = os.path.join( SUBDIR, 'nested.txt' )
        self._makeFile( FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.listDirectory( FILENAME ), None )

    def test_listDirectory_single( self ):

        from string import printable

        SUBDIR = 'subdir'
        FILENAME = os.path.join( SUBDIR, 'nested.txt' )
        self._makeFile( FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        names = ctx.listDirectory( SUBDIR )
        self.assertEqual( len( names ), 1 )
        self.failUnless( 'nested.txt' in names )

    def test_listDirectory_multiple( self ):

        from string import printable
        SUBDIR = 'subdir'
        FILENAME = os.path.join( SUBDIR, 'nested.txt' )
        self._makeFile( FILENAME, printable )
        self._makeFile( os.path.join( SUBDIR, 'another.txt' ), 'ABC' )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        names = ctx.listDirectory( SUBDIR )
        self.assertEqual( len( names ), 2 )
        self.failUnless( 'nested.txt' in names )
        self.failUnless( 'another.txt' in names )

    def test_listDirectory_skip_implicit( self ):

        from string import printable
        SUBDIR = 'subdir'
        FILENAME = os.path.join( SUBDIR, 'nested.txt' )
        self._makeFile( FILENAME, printable )
        self._makeFile( os.path.join( SUBDIR, 'another.txt' ), 'ABC' )
        self._makeFile( os.path.join( SUBDIR, 'CVS/skip.txt' ), 'DEF' )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        names = ctx.listDirectory( SUBDIR )
        self.assertEqual( len( names ), 2 )
        self.failUnless( 'nested.txt' in names )
        self.failUnless( 'another.txt' in names )
        self.failIf( 'CVS' in names )

    def test_listDirectory_skip_explicit( self ):

        from string import printable
        SUBDIR = 'subdir'
        FILENAME = os.path.join( SUBDIR, 'nested.txt' )
        self._makeFile( FILENAME, printable )
        self._makeFile( os.path.join( SUBDIR, 'another.txt' ), 'ABC' )
        self._makeFile( os.path.join( SUBDIR, 'CVS/skip.txt' ), 'DEF' )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        names = ctx.listDirectory( SUBDIR, ( 'nested.txt', ) )
        self.assertEqual( len( names ), 2 )
        self.failIf( 'nested.txt' in names )
        self.failUnless( 'another.txt' in names )
        self.failUnless( 'CVS' in names )


class DirectoryExportContextTests( FilesystemTestBase
                                 , ConformsToISetupContext
                                 , ConformsToIExportContext
                                 ):

    _PROFILE_PATH = '/tmp/ECTTexts'

    def _getTargetClass( self ):

        from Products.CMFSetup.context import DirectoryExportContext
        return DirectoryExportContext

    def test_writeDataFile_simple( self ):

        from string import printable, digits
        FILENAME = 'simple.txt'
        fqname = self._makeFile( FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        ctx.writeDataFile( FILENAME, digits, 'text/plain' )

        self.assertEqual( open( fqname, 'rb' ).read(), digits )

    def test_writeDataFile_new_subdir( self ):

        from string import printable, digits
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        fqname = os.path.join( self._PROFILE_PATH, SUBDIR, FILENAME )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        ctx.writeDataFile( FILENAME, digits, 'text/plain', SUBDIR )

        self.assertEqual( open( fqname, 'rb' ).read(), digits )

    def test_writeDataFile_overwrite( self ):

        from string import printable, digits
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        fqname = self._makeFile( os.path.join( SUBDIR, FILENAME )
                               , printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        ctx.writeDataFile( FILENAME, digits, 'text/plain', SUBDIR )

        self.assertEqual( open( fqname, 'rb' ).read(), digits )

    def test_writeDataFile_existing_subdir( self ):

        from string import printable, digits
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        self._makeFile( os.path.join( SUBDIR, 'another.txt' ), printable )
        fqname = os.path.join( self._PROFILE_PATH, SUBDIR, FILENAME )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        ctx.writeDataFile( FILENAME, digits, 'text/plain', SUBDIR )

        self.assertEqual( open( fqname, 'rb' ).read(), digits )


class TarballExportContextTests( FilesystemTestBase
                               , TarballTester
                               , ConformsToISetupContext
                               , ConformsToIExportContext
                               ):

    _PROFILE_PATH = '/tmp/TECT_tests'

    def _getTargetClass( self ):

        from Products.CMFSetup.context import TarballExportContext
        return TarballExportContext

    def test_writeDataFile_simple( self ):

        from string import printable
        now = long( time.time() )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._getTargetClass()( site )

        ctx.writeDataFile( 'foo.txt', printable, 'text/plain' ) 

        fileish = StringIO( ctx.getArchive() )

        self._verifyTarballContents( fileish, [ 'foo.txt' ], now )
        self._verifyTarballEntry( fileish, 'foo.txt', printable )

    def test_writeDataFile_multiple( self ):

        from string import printable
        from string import digits

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._getTargetClass()( site )

        ctx.writeDataFile( 'foo.txt', printable, 'text/plain' ) 
        ctx.writeDataFile( 'bar.txt', digits, 'text/plain' ) 

        fileish = StringIO( ctx.getArchive() )

        self._verifyTarballContents( fileish, [ 'foo.txt', 'bar.txt' ] )
        self._verifyTarballEntry( fileish, 'foo.txt', printable )
        self._verifyTarballEntry( fileish, 'bar.txt', digits )

    def test_writeDataFile_subdir( self ):

        from string import printable
        from string import digits

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._getTargetClass()( site )

        ctx.writeDataFile( 'foo.txt', printable, 'text/plain' ) 
        ctx.writeDataFile( 'bar/baz.txt', digits, 'text/plain' ) 

        fileish = StringIO( ctx.getArchive() )

        self._verifyTarballContents( fileish, [ 'foo.txt', 'bar/baz.txt' ] )
        self._verifyTarballEntry( fileish, 'foo.txt', printable )
        self._verifyTarballEntry( fileish, 'bar/baz.txt', digits )


class SnapshotExportContextTests( SecurityRequestTest
                                , ConformsToISetupContext
                                , ConformsToIExportContext
                                ):

    def _getTargetClass( self ):

        from Products.CMFSetup.context import SnapshotExportContext
        return SnapshotExportContext

    def _makeOne( self, *args, **kw ):

        return self._getTargetClass()( *args, **kw )

    def test_writeDataFile_simple_image( self ):

        from OFS.Image import Image
        FILENAME = 'simple.txt'
        _CONTENT_TYPE = 'image/png'
        png_filename = os.path.join( os.path.split( __file__ )[0]
                                   , 'simple.png' )
        png_file = open( png_filename, 'rb' )
        png_data = png_file.read()
        png_file.close()

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( FILENAME, png_data, _CONTENT_TYPE )

        snapshot = tool.snapshots._getOb( 'simple' )

        self.assertEqual( len( snapshot.objectIds() ), 1 )
        self.failUnless( FILENAME in snapshot.objectIds() )

        fileobj = snapshot._getOb( FILENAME )

        self.assertEqual( fileobj.getId(), FILENAME )
        self.assertEqual( fileobj.meta_type, Image.meta_type )
        self.assertEqual( fileobj.getContentType(), _CONTENT_TYPE )
        self.assertEqual( fileobj.data, png_data )

    def test_writeDataFile_simple_plain_text( self ):

        from string import digits
        from OFS.Image import File
        FILENAME = 'simple.txt'
        _CONTENT_TYPE = 'text/plain'

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( FILENAME, digits, _CONTENT_TYPE )

        snapshot = tool.snapshots._getOb( 'simple' )

        self.assertEqual( len( snapshot.objectIds() ), 1 )
        self.failUnless( FILENAME in snapshot.objectIds() )

        fileobj = snapshot._getOb( FILENAME )

        self.assertEqual( fileobj.getId(), FILENAME )
        self.assertEqual( fileobj.meta_type, File.meta_type )
        self.assertEqual( fileobj.getContentType(), _CONTENT_TYPE )
        self.assertEqual( str( fileobj ), digits )

    def test_writeDataFile_simple_xml( self ):

        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        FILENAME = 'simple.xml'
        _CONTENT_TYPE = 'text/xml'
        _XML = """<?xml version="1.0"?><simple />"""

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( FILENAME, _XML, _CONTENT_TYPE )

        snapshot = tool.snapshots._getOb( 'simple' )

        self.assertEqual( len( snapshot.objectIds() ), 1 )
        self.failUnless( FILENAME in snapshot.objectIds() )

        template = snapshot._getOb( FILENAME )

        self.assertEqual( template.getId(), FILENAME )
        self.assertEqual( template.meta_type, ZopePageTemplate.meta_type )
        self.assertEqual( template.read(), _XML )
        self.failIf( template.html() )

    def test_writeDataFile_unicode_xml( self ):

        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        FILENAME = 'simple.xml'
        _CONTENT_TYPE = 'text/xml'
        _XML = u"""<?xml version="1.0"?><simple />"""

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( FILENAME, _XML, _CONTENT_TYPE )

        snapshot = tool.snapshots._getOb( 'simple' )

        self.assertEqual( len( snapshot.objectIds() ), 1 )
        self.failUnless( FILENAME in snapshot.objectIds() )

        template = snapshot._getOb( FILENAME )

        self.assertEqual( template.getId(), FILENAME )
        self.assertEqual( template.meta_type, ZopePageTemplate.meta_type )
        self.assertEqual( template.read(), _XML )
        self.failIf( template.html() )

    def test_writeDataFile_subdir_dtml( self ):

        from OFS.DTMLDocument import DTMLDocument
        FILENAME = 'simple.dtml'
        _CONTENT_TYPE = 'text/html'
        _HTML = """<html><body><h1>HTML</h1></body></html>"""

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( FILENAME, _HTML, _CONTENT_TYPE, 'sub1' )

        snapshot = tool.snapshots._getOb( 'simple' )
        sub1 = snapshot._getOb( 'sub1' )

        self.assertEqual( len( sub1.objectIds() ), 1 )
        self.failUnless( FILENAME in sub1.objectIds() )

        template = sub1._getOb( FILENAME )

        self.assertEqual( template.getId(), FILENAME )
        self.assertEqual( template.meta_type, DTMLDocument.meta_type )
        self.assertEqual( template.read(), _HTML )

    def test_writeDataFile_nested_subdirs_html( self ):

        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        FILENAME = 'simple.html'
        _CONTENT_TYPE = 'text/html'
        _HTML = """<html><body><h1>HTML</h1></body></html>"""

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( FILENAME, _HTML, _CONTENT_TYPE, 'sub1/sub2' )

        snapshot = tool.snapshots._getOb( 'simple' )
        sub1 = snapshot._getOb( 'sub1' )
        sub2 = sub1._getOb( 'sub2' )

        self.assertEqual( len( sub2.objectIds() ), 1 )
        self.failUnless( FILENAME in sub2.objectIds() )

        template = sub2._getOb( FILENAME )

        self.assertEqual( template.getId(), FILENAME )
        self.assertEqual( template.meta_type, ZopePageTemplate.meta_type )
        self.assertEqual( template.read(), _HTML )
        self.failUnless( template.html() )

    def test_writeDataFile_multiple( self ):

        from string import printable
        from string import digits

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'multiple' )

        ctx.writeDataFile( 'foo.txt', printable, 'text/plain' ) 
        ctx.writeDataFile( 'bar.txt', digits, 'text/plain' ) 

        snapshot = tool.snapshots._getOb( 'multiple' )

        self.assertEqual( len( snapshot.objectIds() ), 2 )

        for id in [ 'foo.txt', 'bar.txt' ]:
            self.failUnless( id in snapshot.objectIds() )


class SnapshotImportContextTests( SecurityRequestTest
                                , ConformsToISetupContext
                                , ConformsToIImportContext
                                ):

    def _getTargetClass( self ):

        from Products.CMFSetup.context import SnapshotImportContext
        return SnapshotImportContext

    def _makeOne( self, context_id, *args, **kw ):

        site = DummySite( 'site' ).__of__( self.root )
        site._setObject( 'portal_setup', Folder( 'portal_setup' ) )
        tool = site._getOb( 'portal_setup' )

        tool._setObject( 'snapshots', Folder( 'snapshots' ) )
        tool.snapshots._setObject( context_id, Folder( context_id ) )

        ctx = self._getTargetClass()( tool, context_id, *args, **kw )

        return site, tool, ctx.__of__( tool )

    def _makeFile( self
                 , tool
                 , snapshot_id
                 , filename
                 , contents
                 , content_type='text/plain'
                 , mod_time=None
                 , subdir=None
                 ):

        snapshots = tool._getOb( 'snapshots' )
        folder = snapshot = snapshots._getOb( snapshot_id )

        if subdir is not None:

            for element in subdir.split( '/' ):

                try:
                    folder = folder._getOb( element )
                except AttributeError:
                    folder._setObject( element, Folder( element ) )
                    folder = folder._getOb( element )

        file = File( filename, '', contents, content_type )
        folder._setObject( filename, file )

        if mod_time is not None:

            def __faux_mod_time():
                return mod_time

            folder.bobobase_modification_time = \
            file.bobobase_modification_time = __faux_mod_time

        return folder._getOb( filename )

    def test_ctorparms( self ):

        SNAPSHOT_ID = 'ctorparms'
        ENCODING = 'latin-1'
        site, tool, ctx = self._makeOne( SNAPSHOT_ID
                                       , encoding=ENCODING
                                       , should_purge=True
                                       )

        self.assertEqual( ctx.getEncoding(), ENCODING )
        self.assertEqual( ctx.shouldPurge(), True )

    def test_empty( self ):

        SNAPSHOT_ID = 'empty'
        site, tool, ctx = self._makeOne( SNAPSHOT_ID )

        self.assertEqual( ctx.getSite(), site )
        self.assertEqual( ctx.getEncoding(), None )
        self.assertEqual( ctx.shouldPurge(), False )

        # These methods are all specified to return 'None' for non-existing
        # paths / entities
        self.assertEqual( ctx.isDirectory( 'nonesuch/path' ), None )
        self.assertEqual( ctx.listDirectory( 'nonesuch/path' ), None )

    def test_readDataFile_nonesuch( self ):

        SNAPSHOT_ID = 'readDataFile_nonesuch'
        FILENAME = 'nonesuch.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )

        self.assertEqual( ctx.readDataFile( FILENAME ), None )
        self.assertEqual( ctx.readDataFile( FILENAME, 'subdir' ), None )

    def test_readDataFile_simple( self ):

        from string import printable

        SNAPSHOT_ID = 'readDataFile_simple'
        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable )

        self.assertEqual( ctx.readDataFile( FILENAME ), printable )

    def test_readDataFile_subdir( self ):

        from string import printable

        SNAPSHOT_ID = 'readDataFile_subdir'
        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable
                      , subdir=SUBDIR )

        self.assertEqual( ctx.readDataFile( FILENAME, SUBDIR ), printable )

    def test_getLastModified_nonesuch( self ):

        SNAPSHOT_ID = 'getLastModified_nonesuch'
        FILENAME = 'nonesuch.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )

        self.assertEqual( ctx.getLastModified( FILENAME ), None )

    def test_getLastModified_simple( self ):

        from string import printable

        SNAPSHOT_ID = 'getLastModified_simple'
        FILENAME = 'simple.txt'
        WHEN = DateTime( '2004-01-01T00:00:00Z' )

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable
                             , mod_time=WHEN )

        self.assertEqual( ctx.getLastModified( FILENAME ), WHEN )

    def test_getLastModified_subdir( self ):

        from string import printable

        SNAPSHOT_ID = 'getLastModified_subdir'
        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'
        PATH = '%s/%s' % ( SUBDIR, FILENAME )
        WHEN = DateTime( '2004-01-01T00:00:00Z' )

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable
                             , mod_time=WHEN, subdir=SUBDIR )

        self.assertEqual( ctx.getLastModified( PATH ), WHEN )

    def test_getLastModified_directory( self ):

        from string import printable

        SNAPSHOT_ID = 'readDataFile_subdir'
        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'
        WHEN = DateTime( '2004-01-01T00:00:00Z' )

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable
                             , mod_time=WHEN, subdir=SUBDIR )

        self.assertEqual( ctx.getLastModified( SUBDIR ), WHEN )

    def test_isDirectory_nonesuch( self ):

        SNAPSHOT_ID = 'isDirectory_nonesuch'
        FILENAME = 'nonesuch.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )

        self.assertEqual( ctx.isDirectory( FILENAME ), None )

    def test_isDirectory_simple( self ):

        from string import printable

        SNAPSHOT_ID = 'isDirectory_simple'
        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable )

        self.assertEqual( ctx.isDirectory( FILENAME ), False )

    def test_isDirectory_nested( self ):

        from string import printable

        SNAPSHOT_ID = 'isDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        PATH = '%s/%s' % ( SUBDIR, FILENAME )

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable
                             , subdir=SUBDIR )

        self.assertEqual( ctx.isDirectory( PATH ), False )

    def test_isDirectory_subdir( self ):

        from string import printable

        SNAPSHOT_ID = 'isDirectory_subdir'
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        PATH = '%s/%s' % ( SUBDIR, FILENAME )

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable
                             , subdir=SUBDIR )

        self.assertEqual( ctx.isDirectory( SUBDIR ), True )

    def test_listDirectory_nonesuch( self ):

        SNAPSHOT_ID = 'listDirectory_nonesuch'
        SUBDIR = 'nonesuch/path'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )

        self.assertEqual( ctx.listDirectory( SUBDIR ), None )

    def test_listDirectory_root( self ):

        from string import printable

        SNAPSHOT_ID = 'listDirectory_root'
        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable )

        self.assertEqual( len( ctx.listDirectory( None ) ), 1 )
        self.failUnless( FILENAME in ctx.listDirectory( None ) )

    def test_listDirectory_simple( self ):

        from string import printable

        SNAPSHOT_ID = 'listDirectory_simple'
        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable )

        self.assertEqual( ctx.listDirectory( FILENAME ), None )

    def test_listDirectory_nested( self ):

        from string import printable

        SNAPSHOT_ID = 'listDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        PATH = '%s/%s' % ( SUBDIR, FILENAME )

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable
                             , subdir=SUBDIR )

        self.assertEqual( ctx.listDirectory( PATH ), None )

    def test_listDirectory_single( self ):

        from string import printable

        SNAPSHOT_ID = 'listDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file = self._makeFile( tool, SNAPSHOT_ID, FILENAME, printable
                             , subdir=SUBDIR )

        names = ctx.listDirectory( SUBDIR )
        self.assertEqual( len( names ), 1 )
        self.failUnless( FILENAME in names )

    def test_listDirectory_multiple( self ):

        from string import printable, uppercase

        SNAPSHOT_ID = 'listDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME1 = 'nested.txt'
        FILENAME2 = 'another.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file1 = self._makeFile( tool, SNAPSHOT_ID, FILENAME1, printable
                              , subdir=SUBDIR )
        file2 = self._makeFile( tool, SNAPSHOT_ID, FILENAME2, uppercase
                              , subdir=SUBDIR )

        names = ctx.listDirectory( SUBDIR )
        self.assertEqual( len( names ), 2 )
        self.failUnless( FILENAME1 in names )
        self.failUnless( FILENAME2 in names )

    def test_listDirectory_skip( self ):

        from string import printable, uppercase

        SNAPSHOT_ID = 'listDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME1 = 'nested.txt'
        FILENAME2 = 'another.txt'

        site, tool, ctx = self._makeOne( SNAPSHOT_ID )
        file1 = self._makeFile( tool, SNAPSHOT_ID, FILENAME1, printable
                              , subdir=SUBDIR )
        file2 = self._makeFile( tool, SNAPSHOT_ID, FILENAME2, uppercase
                              , subdir=SUBDIR )

        names = ctx.listDirectory( SUBDIR, skip=( FILENAME1, ) )
        self.assertEqual( len( names ), 1 )
        self.failIf( FILENAME1 in names )
        self.failUnless( FILENAME2 in names )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( DirectoryImportContextTests ),
        unittest.makeSuite( DirectoryExportContextTests ),
        unittest.makeSuite( TarballExportContextTests ),
        unittest.makeSuite( SnapshotExportContextTests ),
        unittest.makeSuite( SnapshotImportContextTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
