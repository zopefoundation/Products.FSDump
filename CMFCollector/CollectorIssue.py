##############################################################################
# Copyright (c) 2001 Zope Corporation.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 1.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
##############################################################################

"""Implement the Collector Issue content type - a bundle containing the
collector transcript and various parts."""

import os, urllib, string, re
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base

import util                             # Collector utilities.

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFDefault.Document import addDocument

# Import permission names
from Products.CMFCore import CMFCorePermissions
from CollectorPermissions import *

DEFAULT_TRANSCRIPT_FORMAT = 'stx'

factory_type_information = (
    {'id': 'Collector Issue',
#XXX     'content_icon': 'event_icon.gif',
     'meta_type': 'CMF Collector Issue',
     'description': ('A Collector Issue represents a bug report or'
                     ' other support request.'),
     'product': 'CMFCollector',
     'factory': None,                   # So not included in 'New' add form
     'allowed_content_types': ('Collector Issue Transcript', 'File', 'Image'), 
     'immediate_view': 'collector_edit_form',
     'actions': ({'id': 'view',
                  'name': 'Transcript',
                  'action': 'collector_issue_contents',
                  'permissions': (ViewCollector,)},
                 {'id': 'followup',
                  'name': 'Followup',
                  'action': 'collector_issue_followup_form',
                  'permissions': (AddCollectorIssueComment,)},
                 {'id': 'artifacts',
                  'name': 'Add Artifacts',
                  'action': 'collector_issue_add_artifact_form',
                  'permissions': (AddCollectorIssueArtifact,)},
                 {'id': 'edit',
                  'name': 'Edit Issue',
                  'action': 'collector_issue_edit_form',
                  'permissions': (EditCollectorIssue,)},
                 {'id': 'browse',
                  'name': 'Browse Collector',
                  'action': 'collector_issue_up',
                  'permissions': (ViewCollector,)},
                 {'id': 'addIssue',
                  'name': 'New Issue',
                  'action': 'collector_issue_add_issue',
                  'permissions': (ViewCollector,)},
                 ),
     },
    )

TRANSCRIPT_NAME = "ISSUE_TRANSCRIPT"

class CollectorIssue(SkinnedFolder, DefaultDublinCoreImpl):
    """An individual support request in the CMF Collector."""

    meta_type = 'CMF Collector Issue'
    effective_date = expiration_date = None
    
    security = ClassSecurityInfo()

    comment_delimiter = "<hr solid id=comment_delim>"

    comment_number = 0

    def __init__(self, 
                 id, container,
                 title='', description='',
                 submitter_id=None, submitter_name=None, submitter_email=None,
                 kibitzers=None,
                 topic=None, classification=None,
                 security_related=0,
                 importance=None, severity=None,
                 assigned_to=None, current_status='pending',
                 resolution=None,
                 reported_version=None, other_version_info=None,
                 creation_date=None, modification_date=None,
                 effective_date=None, expiration_date=None):
        """ """

        SkinnedFolder.__init__(self, id, title)
        # Take care of standard metadata:
        DefaultDublinCoreImpl.__init__(self,
                                       title=title, description=description,
                                       effective_date=effective_date,
                                       expiration_date=expiration_date)
        if modification_date is None:
            modification_date = self.creation_date
        self.modification_date = modification_date

        self._create_transcript(description, container)

        user = getSecurityManager().getUser()
        if submitter_id is None:
            self.submitter_id = str(user)
        self.submitter_id = submitter_id
        if submitter_name is None:
            if hasattr(user, 'full_name'):
                submitter_name = user.full_name
        elif (submitter_name
              and (getattr(user, 'full_name', None) != submitter_name)):
            # XXX We're being cavalier about stashing the full_name.
            user.full_name = submitter_name
        self.submitter_name = submitter_name
        if submitter_email is None and hasattr(user, 'email'):
            submitter_email = user.email
        self.submitter_email = submitter_email

        if kibitzers is None:
            kibitzers = ()
        self.kibitzers = kibitzers

        self.topic = topic
        self.classification = classification
        self.security_related = security_related
        self.importance = importance
        self.severity = severity
        self.assigned_to = assigned_to
        self.current_status = current_status
        self.resolution = resolution
        self.reported_version = reported_version
        self.other_version_info = other_version_info

        self.edited = 0

        return self

    security.declareProtected(EditCollectorIssue, 'edit')
    def edit(self, comment=None,
             text=None,
             status=None,
             submitter_name=None,
             title=None,
             description=None,
             security_related=None,
             topic=None,
             importance=None,
             classification=None,
             severity=None,
             reported_version=None,
             other_version_info=None):
        """Update the explicitly passed fields."""
        if text is not None:
            transcript = self.get_transcript()
            transcript._edit(text_format=DEFAULT_TRANSCRIPT_FORMAT,
                             text=text)
        if comment is not None:
            self.do_action('edit', comment)
        if submitter_name is not None:
            self.submitter_name = submitter_name
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if security_related is not None:
            self.security_related = security_related
        if topic is not None:
            self.topic = topic
        if importance is not None:
            self.importance = importance
        if classification is not None:
            self.classification = classification
        if severity is not None:
            self.severity = severity
        if reported_version is not None:
            self.reported_version = reported_version
        if other_version_info is not None:
            self.other_version_info = other_version_info
        self.edited = 1

    security.declareProtected(CMFCorePermissions.View, 'get_transcript')
    def get_transcript(self):
        return self._getOb(TRANSCRIPT_NAME)

    security.declareProtected(AddCollectorIssueComment, 'do_action')
    def do_action(self, action, comment, attachments=None):
        """Execute an action, adding comment to the transcript."""
        transcript = self.get_transcript()
        self.comment_number = self.comment_number + 1
        entry_leader = "\n\n" + self._entry_header(action) + "\n\n"
        transcript._edit('stx',
                         transcript.EditableBody()
                         + entry_leader
                         + util.process_comment(comment))

    security.declareProtected(AddCollectorIssueArtifact, 'add_artifact')
    def add_artifact(self, id, type, description, file):
        """Add new artifact, and note in transcript."""
        self.invokeFactory(type, id)
        it = self._getOb(id)
        it.description = description
        it.manage_upload(file)
        transcript = self.get_transcript()
        entry_leader = ("\n\n"
                        + self._entry_header("New Artifact '%s'" % id)
                        + "\n\n")
        transcript._edit('stx',
                         transcript.EditableBody()
                         + entry_leader
                         + util.process_comment(description))

    def _create_transcript(self, description, container,
                           text_format=DEFAULT_TRANSCRIPT_FORMAT):
        """Create events and comments transcript, with initial entry."""

        addDocument(self, TRANSCRIPT_NAME, description=description)
        it = self.get_transcript()
        it._setPortalTypeName('Collector Issue Transcript')
        text = "%s\n\n %s " % (self._entry_header('Request', prefix="== "),
                               description)
        it._edit(text_format=text_format, text=text)
        it.title = self.title

    def _entry_header(self, type, prefix="<hr> == ", suffix=" =="):
        """Return text for the header of a new transcript entry."""
        # Ideally this would be a skin method (probly python script), but i
        # don't know how to call it from the product, sigh.
        t = string.capitalize(type)
        if self.comment_number:
            lead = t + " - Entry #" + str(self.comment_number)
        else:
            lead = t

        user = getSecurityManager().getUser()
        return ("%s%s by %s on %s%s" %
                (prefix, lead, str(user), DateTime().aCommon(), suffix))

    security.declareProtected(CMFCorePermissions.View, 'cited_text')
    def cited_text(self):
        """Quote text for use in literal citations."""
        return util.cited_text(self.get_transcript().text)

    #################################################
    # Dublin Core and search provisions

    # The transcript indexes itself, we just need to index the salient
    # attribute-style issue data/metadata...

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'indexObject')
    def indexObject(self):
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.indexObject(self)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'unindexObject')
    def unindexObject(self):
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.unindexObject(self)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'reindexObject')
    def reindexObject(self):
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.reindexObject(self)

    def manage_afterAdd(self, item, container):
        """Add self to the workflow and catalog."""
        # Are we being added (or moved)?
        if aq_base(container) is not aq_base(self):
            wf = getToolByName(self, 'portal_workflow', None)
            if wf is not None:
                wf.notifyCreated(self)
            self.indexObject()

    def manage_beforeDelete(self, item, container):
        """Remove self from the catalog."""
        # Are we going away?
        if aq_base(container) is not aq_base(self):
            self.unindexObject()
            # Now let our "aspects" know we are going away.
            for it, subitem in self.objectItems():
                si_m_bD = getattr(subitem, 'manage_beforeDelete', None)
                if si_m_bD is not None:
                    si_m_bD(item, container)

    def SearchableText(self):
        """Consolidate all text and structured fields for catalog search."""
        # Make this a composite of the text and structured fields.
        return (self.title + ' '
                + self.description + ' '
                + self.topic + ' '
                + self.classification + ' '
                + self.importance + ' '
                + self.severity + ' '
                + self.current_status + ' '
                + self.resolution + ' '
                + self.reported_version + ' '
                + self.other_version_info + ' '
                + ((self.security_related and 'security_related') or ''))

    def Subject(self):
        """The structured attrs, combined w/field names for targeted search."""
        return ('topic:' + self.topic,
                'classification:' + self.classification,
                'security_related:' + ((self.security_related and '1') or '0'),
                'importance:' + self.importance,
                'severity:' + self.severity,
                'assigned_to:' + (self.assigned_to or ''),
                'current_status:' + (self.current_status or ''),
                'resolution:' + (self.resolution or ''),
                'reported_version:' + self.reported_version)

    def __repr__(self):
        return ("<%s %s \"%s\" at 0x%s>"
                % (self.__class__.__name__,
                   self.id, self.title,
                   hex(id(self))[2:]))

InitializeClass(CollectorIssue)
    

def addCollectorIssue(self,
                      id,
                      title='',
                      description='',
                      submitter_id=None,
                      submitter_name=None,
                      submitter_email=None,
                      kibitzers=None,
                      topic=None,
                      classification=None,
                      security_related=0,
                      importance=None,
                      severity=None,
                      assigned_to=None,
                      reported_version=None,
                      other_version_info=None,
                      REQUEST=None):
    """
    Create a new issue in the collector.
    """

    it = CollectorIssue(id=id,
                        container=self,
                        title=title,
                        description=description,
                        submitter_id=submitter_id,
                        submitter_name=submitter_name,
                        submitter_email=submitter_email,
                        kibitzers=kibitzers,
                        topic=topic,
                        classification=classification,
                        security_related=security_related,
                        importance=importance,
                        severity=severity,
                        assigned_to=assigned_to,
                        reported_version=reported_version,
                        other_version_info=other_version_info)
    it._setPortalTypeName('Collector Issue')
    self._setObject(id, it)
    return id
