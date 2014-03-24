# Security extensions


zojax security mechanism is based on zope's one, providing its own extensions,
including pluggable security grants.


## Pluggable permission grants


Standard zope security policy mechanism uses single security map for an object
providing a way to override it by supplying own map adapter. Unlike zope, zojax
extended security policy supports multiple principal<->role<->permission map
adapters merging their grants to make a final decisions.

To provide a principal-role map plugin, we need to implement a custom
``IPrincipalRoleMap`` adapter. For example, we can implement a plugin that
sets the owner role for a principal that owns an object:

    from zope.securitypolicy.interfaces import IPrincipalRoleMap
    from zope.securitypolicy.interfaces import Allow, Deny

    class OwnershipRoleMap(object):
        implements(IPrincipalRoleMap)

        def __init__(self, context):
            self.owner_id = context.owner # get the id of the owner principal

        def getPrincipalsForRole(self, role_id):
            if role_id == 'custom.Owner':
                return ((self.owner_id, Allow), )
            return ()

        def getRolesForPrincipal(self, principal_id):
            if principal_id == self.owner_id:
                return (('custom.Owner', Allow), )
            return (('custom.Owner', Deny), )

        def getSetting(self, role_id, principal_id):
            if (role_id == 'custom.Owner') and (principal_id == self.owner_id):
                return Allow
            return Deny

        def getPrincipalsAndRoles(self):
            return (('custom.Owner', principal_id, Allow), )

This example is pretty like zojax ownership implementation. As you can see, it's
a simple implementation of standard principal-role map defined by zope security
policy. The main difference is that it only handles settings related to
``custom.Owner`` role and its settings will be merged with other principal-role
adapters to create finel principal-role mapping for use in grant decisions.

Now, we need to register this security map plugin as a named adapter using standard
zope ``adapter`` directive:

    <adapter
        for=".interfaces.ISomeOwnershipAwareContent"
        name="ownership"
        factory=".OwnershipRoleMap"
        />

The plugins for other security map types (role-permission and principal-permission)
are done just the same way: implement an adapter, register it with some name.
