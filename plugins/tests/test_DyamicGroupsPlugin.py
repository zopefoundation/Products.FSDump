##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Unit tests for DynamicGroupsPlugin

$Id$
"""
import unittest


from Products.PluggableAuthService.tests.conformance \
    import IGroupsPlugin_conformance

from Products.PluggableAuthService.tests.conformance \
    import IGroupEnumerationPlugin_conformance

class FauxScript:


    def __init__( self, id, return_value=0 ):

        self._id = id
        self.return_value = return_value

    def __call__( self, *args, **kw ):

        return self.return_value

class FauxPrincipal:

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__( self, id ):
        self._id = id

    def getId( self ):
        return self._id

class DynamicGroupsPlugin( unittest.TestCase
                         , IGroupsPlugin_conformance 
                         , IGroupEnumerationPlugin_conformance
                         ):


    def _getTargetClass( self ):

        from Products.PluggableAuthService.plugins.DynamicGroupsPlugin \
            import DynamicGroupsPlugin

        return DynamicGroupsPlugin

    def _makeOne( self, id='test', *args, **kw ):

        return self._getTargetClass()( id, *args, **kw )

    def test_empty( self ):

        dpg = self._makeOne( 'empty' )

        self.assertEqual( len( dpg.listGroupIds() ), 0 )
        self.assertEqual( len( dpg.listGroupInfo() ), 0 )
        self.assertEqual( len( dpg.enumerateGroups() ), 0 )

    def test_addGroup_simple( self ):

        dpg = self._makeOne( 'adding' )

        dpg.addGroup( 'everyone', 'python:True', 'title', 'description', True )

        self.assertEqual( len( dpg.listGroupIds() ), 1 )
        self.failUnless( 'everyone' in dpg.listGroupIds() )

        self.assertEqual( len( dpg.listGroupInfo() ), 1 )
        info = dpg.listGroupInfo()[0]

        self.assertEqual( info[ 'id' ], 'everyone' )
        self.assertEqual( info[ 'title' ], 'title' )
        self.assertEqual( info[ 'description' ], 'description' )
        self.assertEqual( info[ 'predicate' ], 'python:True' )
        self.assertEqual( info[ 'active' ], True )

    def test_addGroup_duplicate( self ):

        dpg = self._makeOne( 'adding_duplicate' )

        dpg.addGroup( 'everyone', 'python:True', 'title', 'description', True )

        self.assertRaises( KeyError
                         , dpg.addGroup
                         , 'everyone'
                         , 'python:False'
                         , 'other title'
                         , 'other descripton'
                         , False )

        self.assertEqual( len( dpg.listGroupInfo() ), 1 )
        info = dpg.listGroupInfo()[0]

        self.assertEqual( info[ 'id' ], 'everyone' )
        self.assertEqual( info[ 'predicate' ], 'python:True' )
        self.assertEqual( info[ 'title' ], 'title' )
        self.assertEqual( info[ 'description' ], 'description' )
        self.assertEqual( info[ 'active' ], True )

    def test_removeGroup_nonesuch( self ):

        dpg = self._makeOne( 'removing_nonesuch' )

        self.assertRaises( KeyError, dpg.removeGroup, 'everyone' )

    def test_removeGroup( self ):

        dpg = self._makeOne( 'removing' )

        dpg.addGroup( 'everyone', predicate='python:True' )
        dpg.addGroup( 'beast', predicate='python:666' )
        dpg.addGroup( 'noone', predicate='python:False' )

        self.assertEqual( len( dpg.listGroupIds() ), 3 )
        self.failUnless( 'everyone' in dpg.listGroupIds() )
        self.failUnless( 'beast' in dpg.listGroupIds() )
        self.failUnless( 'noone' in dpg.listGroupIds() )

        info_list = dpg.listGroupInfo()
        self.assertEqual( len( info_list ), 3 )

        ids = [ x[ 'id' ] for x in info_list ]
        self.failUnless( 'everyone' in ids )
        self.failUnless( 'beast' in ids )
        self.failUnless( 'noone' in ids )

        dpg.removeGroup( 'beast' )

        self.assertEqual( len( dpg.listGroupIds() ), 2 )
        self.failUnless( 'everyone' in dpg.listGroupIds() )
        self.failIf( 'beast' in dpg.listGroupIds() )
        self.failUnless( 'noone' in dpg.listGroupIds() )

        info_list = dpg.listGroupInfo()
        self.assertEqual( len( info_list ), 2 )

        ids = [ x[ 'id' ] for x in info_list ]
        self.failUnless( 'everyone' in ids )
        self.failIf( 'beast' in ids )
        self.failUnless( 'noone' in ids )

    def test_updateGroup_nonesuch( self ):

        dpg = self._makeOne( 'updating_nonesuch' )

        self.assertRaises( KeyError, dpg.updateGroup
                         , 'everyone', 'title', True )

    def test_updateGroup_simple( self ):

        dpg = self._makeOne( 'updating_simple' )

        dpg.addGroup( 'noone', predicate='python:False' )

        self.assertEqual( len( dpg.listGroupIds() ), 1 )
        self.failUnless( 'noone' in dpg.listGroupIds() )

        self.assertEqual( len( dpg.listGroupInfo() ), 1 )
        info = dpg.listGroupInfo()[0]

        self.assertEqual( info[ 'id' ], 'noone' )
        self.assertEqual( info[ 'predicate' ], 'python:False' )
        self.assertEqual( info[ 'title' ], '' )
        self.assertEqual( info[ 'description' ], '' )
        self.assertEqual( info[ 'active' ], True )

        dpg.updateGroup( 'noone', 'python:True', 'title', 'description', False )

        self.assertEqual( len( dpg.listGroupIds() ), 1 )
        self.failUnless( 'noone' in dpg.listGroupIds() )

        self.assertEqual( len( dpg.listGroupInfo() ), 1 )
        info = dpg.listGroupInfo()[0]

        self.assertEqual( info[ 'id' ], 'noone' )
        self.assertEqual( info[ 'predicate' ], 'python:True' )
        self.assertEqual( info[ 'title' ], 'title' )
        self.assertEqual( info[ 'description' ], 'description' )
        self.assertEqual( info[ 'active' ], False )

    def test_updateGroup_partial( self ):

        dpg = self._makeOne( 'updating_partial' )

        dpg.addGroup( 'everyone', 'python:True', 'title', 'description', True )

        self.assertEqual( len( dpg.listGroupIds() ), 1 )
        self.failUnless( 'everyone' in dpg.listGroupIds() )

        self.assertEqual( len( dpg.listGroupInfo() ), 1 )
        info = dpg.listGroupInfo()[0]

        self.assertEqual( info[ 'id' ], 'everyone' )
        self.assertEqual( info[ 'predicate' ], 'python:True' )
        self.assertEqual( info[ 'title' ], 'title' )
        self.assertEqual( info[ 'description' ], 'description' )
        self.assertEqual( info[ 'active' ], True )

        dpg.updateGroup( 'everyone', predicate='python:False' )

        self.assertEqual( len( dpg.listGroupIds() ), 1 )
        self.failUnless( 'everyone' in dpg.listGroupIds() )

        self.assertEqual( len( dpg.listGroupInfo() ), 1 )
        info = dpg.listGroupInfo()[0]

        self.assertEqual( info[ 'id' ], 'everyone' )
        self.assertEqual( info[ 'predicate' ], 'python:False' )
        self.assertEqual( info[ 'title' ], 'title' )
        self.assertEqual( info[ 'description' ], 'description' )
        self.assertEqual( info[ 'active' ], True )

    def test_enumerateGroups_all( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        dpg = self._makeOne( 'enumerating' ).__of__( root )

        dpg.addGroup( 'everyone', 'python:True', 'Everyone', '', True )
        dpg.addGroup( 'noone', 'python:False', active=True )
        dpg.addGroup( 'hohum', 'nothing', active=True )

        info_list = dpg.enumerateGroups()

        self.assertEqual( len( info_list ), 3 )

        ids = [ x[ 'id' ] for x in info_list ]

        self.failUnless( 'everyone' in ids )
        self.failUnless( 'noone' in ids )
        self.failUnless( 'hohum' in ids )

    def test_enumerateGroups_exact_list( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        dpg = self._makeOne( 'enumerating' ).__of__( root )

        dpg.addGroup( 'everyone', 'python:True', 'Everyone', '', True )
        dpg.addGroup( 'noone', 'python:False', active=True )
        dpg.addGroup( 'hohum', 'nothing', active=True )

        ID_LIST = ( 'everyone', 'noone' )

        info_list = dpg.enumerateGroups( id=ID_LIST, exact_match=True )

        self.assertEqual( len( info_list ), len( ID_LIST ) )

        ids = [ x[ 'id' ] for x in info_list ]

        for id in ID_LIST:
            self.failUnless( id in ids )

    def test_enumerateGroups_exact_one( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        dpg = self._makeOne( 'enumerating' ).__of__( root )

        dpg.addGroup( 'everyone', 'python:True', 'Everyone', '', True )
        dpg.addGroup( 'noone', 'python:False', active=True )
        dpg.addGroup( 'hohum', 'nothing', active=True )

        info_list = dpg.enumerateGroups( id='noone', exact_match=True )

        self.assertEqual( len( info_list ), 1 )
        info = info_list[ 0 ]

        self.assertEqual( info[ 'id' ], 'noone' )
        self.assertEqual( info[ 'title' ], '' )
        self.assertEqual( info[ 'description' ], '' )
        self.assertEqual( info[ 'active' ], True )
        self.assertEqual( info[ 'predicate' ], 'python:False' )
        self.assertEqual( info[ 'pluginid' ], 'enumerating' )

        URL = '/enumerating/noone/manage_propertiesForm'
        self.assertEqual( info[ 'properties_url' ], URL )
        self.assertEqual( info[ 'members_url' ], URL )

    def test_enumerateGroups_skip_inactive( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        dpg = self._makeOne( 'enumerating' ).__of__( root )

        dpg.addGroup( 'everyone', 'python:True', 'Everyone', '', True )
        dpg.addGroup( 'noone', 'python:False', active=True )
        dpg.addGroup( 'inactive', 'nothing', active=False )

        info_list = dpg.enumerateGroups()

        self.assertEqual( len( info_list ), 2 )

        ids = [ x[ 'id' ] for x in info_list ]

        self.failUnless( 'everyone' in ids )
        self.failUnless( 'noone' in ids )
        self.failIf( 'inactive' in ids )

    def test_getGroupsForPrincipal_empty( self ):

        dpg = self._makeOne( 'ggp_request' )
        principal = FauxPrincipal( 'faux' )
        
        groups = dpg.getGroupsForPrincipal( principal )

        self.assertEqual( len( groups ), 0 )

    def test_getGroupsForPrincipal_principal( self ):

        dpg = self._makeOne( 'ggp_principal' )
        principal = FauxPrincipal( 'faux' )
        
        dpg.addGroup( 'effable', 'python:principal.getId().startswith("f")' )
        groups = dpg.getGroupsForPrincipal( principal, {} )
        self.assertEqual( len( groups ), 1 )
        self.failUnless( 'effable' in groups )

    def test_getGroupsForPrincipal_python( self ):

        dpg = self._makeOne( 'ggp_python' )
        principal = FauxPrincipal( 'faux' )
        
        dpg.addGroup( 'everyone', 'python:1' )
        groups = dpg.getGroupsForPrincipal( principal, {} )
        self.assertEqual( len( groups ), 1 )
        self.failUnless( 'everyone' in groups )

    def test_getGroupsForPrincipal_request( self ):

        dpg = self._makeOne( 'ggp_request' )
        principal = FauxPrincipal( 'faux' )
        
        dpg.addGroup( 'local', 'request/is_local | nothing' )

        groups = dpg.getGroupsForPrincipal( principal, {} )

        self.assertEqual( len( groups ), 0 )

        groups = dpg.getGroupsForPrincipal( principal, { 'is_local' : 0 } )

        self.assertEqual( len( groups ), 0 )

        groups = dpg.getGroupsForPrincipal( principal, { 'is_local' : 1 } )

        self.assertEqual( len( groups ), 1 )
        self.failUnless( 'local' in groups )

    def test_getGroupsForPrincipal_group( self ):

        dpg = self._makeOne( 'ggp_group' )
        principal = FauxPrincipal( 'faux' )
        
        dpg.addGroup( 'willing', 'group/willing' )
        dpg.willing._setProperty( 'willing', type='boolean', value=0 )

        groups = dpg.getGroupsForPrincipal( principal, {} )
        self.assertEqual( len( groups ), 0 )

        dpg.willing._updateProperty( 'willing', 1 )
        groups = dpg.getGroupsForPrincipal( principal, {} )
        self.assertEqual( len( groups ), 1 )
        self.failUnless( 'willing' in groups )

    def test_getGroupsForPrincipal_plugin_nope( self ):

        dpg = self._makeOne( 'ggp_plugin' )
        principal = FauxPrincipal( 'faux' )
        
        dpg.addGroup( 'scripted', 'python: plugin.callme(request)' )
        callme = FauxScript( 'callme', 0 )
        dpg._setOb( 'callme', callme )

        groups = dpg.getGroupsForPrincipal( principal, {} )
        self.assertEqual( len( groups ), 0 )

    def test_getGroupsForPrincipal_plugin_ok( self ):

        dpg = self._makeOne( 'ggp_plugin' )
        principal = FauxPrincipal( 'faux' )
        
        dpg.addGroup( 'scripted', 'python: plugin.callme(request)' )
        callme = FauxScript( 'callme', 1 )
        dpg._setOb( 'callme', callme )

        groups = dpg.getGroupsForPrincipal( principal, {} )
        self.assertEqual( len( groups ), 1 )
        self.failUnless( 'scripted' in groups )
