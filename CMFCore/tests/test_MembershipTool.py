from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.tests.base.dummy import DummyFolder as DummyFolderBase
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.testcase import SecurityTest

from Products.CMFCore.MembershipTool import MembershipTool


class DummyFolder(DummyFolderBase):
    def _getProductRegistryData(self, name):
        return ()
    def getPhysicalRoot(self):
        return self
    def unrestrictedTraverse(self, path, default=None, restricted=0):
        return self.acl_users


class MembershipToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_membership \
                import portal_membership as IMembershipTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IMembershipTool, MembershipTool)
        verifyClass(IActionProvider, MembershipTool)


class MembershipToolSecurityTests(SecurityTest):

    def setUp(self):
        SecurityTest.setUp(self)
        self.site = DummyFolder()
        self.site.id = 'testSite'
        self.mtool = MembershipTool().__of__(self.site)

    def test_createMemberarea(self):
        mtool = self.mtool
        self.site._setObject( 'Members', PortalFolder('Members') )
        self.site._setObject( 'acl_users', DummyUserFolder() )
        self.site._setObject( 'portal_workflow', DummyTool() )
        mtool.createMemberarea('user_foo')

        f = self.site.Members.user_foo
        ownership = self.site.acl_users.user_foo
        localroles = ( ( 'user_foo', ('Owner',) ), )
        self.assertEqual( f.getOwner(), ownership )
        self.assertEqual( f.get_local_roles(), localroles,
                          'CMF Collector issue #162 (LocalRoles broken): %s'
                          % str( f.get_local_roles() ) )


def test_suite():
    return TestSuite((
        makeSuite( MembershipToolTests ),
        makeSuite( MembershipToolSecurityTests )
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
