import Zope
from unittest import TestCase, TestSuite, makeSuite, main
from Products.CMFCore.DirectoryView import \
     registerDirectory,addDirectoryViews,DirectoryViewSurrogate
from Globals import package_home, DevelopmentMode
from Acquisition import Implicit
from os import remove, mkdir, rmdir
from os.path import join
from shutil import copy2

# the path of our fake skin
skin_path_name = join(package_home(globals()),'fake_skins','fake_skin')

class DirectoryViewTests1( TestCase ):

    def test_registerDirectory( self ):
        """ Test registerDirectory  """
        registerDirectory('fake_skins', globals())

class Dummy(Implicit):
    """
    A Dummy object to use in place of the skins tool
    """

    def _setObject(self,id,object):
        """ Dummy _setObject method """
        setattr(self,id,object)

class DirectoryViewTests2( TestCase ):

    def setUp( self ):
        registerDirectory('fake_skins', globals())
        ob = self.ob = Dummy()
        addDirectoryViews(ob, 'fake_skins', globals())

    def test_addDirectoryViews( self ):
        """ Test addDirectoryViews  """
        pass

    def test_DirectoryViewExists( self ):
        """
        Check DirectoryView added by addDirectoryViews
        appears as a DirectoryViewSurrogate due
        to Acquisition hackery.
        """
        self.failUnless(isinstance(self.ob.fake_skin,DirectoryViewSurrogate))

    def test_DirectoryViewMethod( self ):
        """ Check if DirectoryView method works """
        self.assertEqual(self.ob.fake_skin.test1(),'test1')

test1path = join(skin_path_name,'test1.py')
test2path = join(skin_path_name,'test2.py')
test3path = join(skin_path_name,'test3')

if DevelopmentMode:

  class DebugModeTests( TestCase ):

    def setUp( self ):
        
        # initialise skins
        registerDirectory('fake_skins', globals())
        ob = self.ob = Dummy()
        addDirectoryViews(ob, 'fake_skins', globals())

        # add a method to the fake skin folder
        f = open(test2path,'w')
        f.write("return 'test2'")
        f.close()

        # edit the test1 method
        copy2(test1path,test1path+'.bak')
        f = open(test1path,'w')
        f.write("return 'new test1'")
        f.close()

        # add a new folder
        mkdir(test3path)
        
    def tearDown( self ):
        
        # undo FS changes
        remove(test1path)
        copy2(test1path+'.bak',test1path)
        remove(test1path+'.bak')
        try:        
            remove(test2path)
        except (IOError,OSError):
            # it might be gone already
            pass
        try:
            rmdir(test3path)
        except (IOError,OSError):
            # it might be gone already
            pass
        
    def test_AddNewMethod( self ):
        """
        See if a method added to the skin folder can be found
        """
        self.assertEqual(self.ob.fake_skin.test2(),'test2')

    def test_EditMethod( self ):
        """
        See if an edited method exhibits its new behaviour
        """
        self.assertEqual(self.ob.fake_skin.test1(),'new test1')

    def test_NewFolder( self ):
        """
        See if a new folder shows up
        """
        # This fails for some bizarre reason :-( - CW
        self.failUnless(isinstance(self.ob.fake_skin.test3,DirectoryViewSurrogate))
        self.ob.fake_skin.test3.objectIds()

    def test_DeleteMethod( self ):
        """
        Make sure a deleted method goes away
        """
        remove(test2path)
        try:
            self.ob.fake_skin.test2
        except AttributeError:
            pass
        else:
            self.fail('test2 still exists')

    def test_DeleteFolder( self ):
        """
        Make sure a deleted folder goes away
        """
        rmdir(test3path)
        try:
            self.ob.fake_skin.test3
        except AttributeError:
            pass
        else:
            self.fail('test3 still exists')

else:

    class DebugModeTests( TestCase ):
        pass

def test_suite():
    return TestSuite((
        makeSuite(DirectoryViewTests1),
        makeSuite(DirectoryViewTests2),
        makeSuite(DebugModeTests),
        ))

def run():
    main(defaultTest='test_suite')

if __name__ == '__main__':
    run()



