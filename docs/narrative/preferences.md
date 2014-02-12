# User preferences


The ``zojax.preferences`` package implements a method to easily add custom
principal preferences in a single way, automatically providing browser menus
and edit forms for these preferences.

The preferences are organized in hierarchical way to ease navigation between
them, so each group of preferences can have multiple children groups. Those
"preference groups" is what a developer creates.

Though the package is made very flexible, the basic usage is very simple.


## Basic usage


If you simply want to store some user-specific data and make it automaically
editable by user, you need to:

1. Define a preference group schema (just like any zope schema - an interface
   with zope.schema fields defined in it). Example:

        class ISimpleProfile(zope.interface.Interface):

           birthDate = Date(title=u'Birth Date', required=True)
           signature = Text(title=u'Signature', required=False)

2. Register it using the ``zojax:preferenceGroup`` ZCML directive. Example:

        <zojax:preferenceGroup
          id="simpleprofile"
          title="Simple Profile"
          schema=".interfaces.ISimpleProfile"
          />

The ZCML directive have three required arguments: **id**, **title** and **schema**. While
``title`` and ``schema`` are self-explanatory, the ``id`` argument have its
catches. First, as it's clear from the name, it should be unique identifier
of the group. Second, because preference groups are hierarchical, dot symbol
in the id has a special meaning.

In the example above, we don't have any dots in the id. It means that this
preference group will be added to the root group, it can be thinked of as
the "top-level" group. However, if we will create another preference group
with, for example, "simpleprofile.moreinfo" as the id, the new group is added
as a child to our "simpleprofile" group and it's menu item will be rendered
as a sub-menu item under the "Simple Profile".

There is no restriction on the depth of preference group nesting, but remember
that you should always register parent groups before registering child groups.

After registering the preference group, a principal (IPrincipal object)
can be adapted to an interface used as a preference group schema (which is
ISimpleProfile in our examples above) and the values for fields defined in
the schema can be get and set. The preferences mechanism handles storage of
that values itself.

The preference groups can also be looked up as a named utility providing
``zojax.preferences.interfaces.IPreferenceGroup`` interface using the group id
as a name. However, those groups are not bound to any principal and their
attributes can not be got or set. To bind an unbound group to a principal, you
can use the ``__bind__`` method, passing the principal object as the argument.

**Note:**

>   The preference group objects are not persistent and only those attributes
   will be stored by default that are defined in the preference group schema.


The browser UI for editing principal preferences are available as view named
"preferences" for the site objects (objects providing
``zope.app.component.interfaces.ISite`` interface). So if your site root is at
"http://yoursiteurl.com", the preferences UI will be available at
"http://yoursiteurl.com/preferences".


## Advanced usage


### ZCML directive


The ``zojax:preferenceGroup`` ZCML directive has more arguments that can be
used to make a more specific preference group. Let's describe them all:

* **id** - The unique identifier of a preference group. Group hierarchy is organized
  using dots in the ids (see above).

* **for** - An interface of principal objects that will have this preference group.
  This allows preferences to be available only specific principal types.

* **schema** - Preference schema interface. By default, storable properties will be
  created only for fields defined in this schema. It makes sense to use an
  empty interface as the schema, in case you want the preference group to be
  registered and provide custom data storage mechanism and browser views.

* **title** - Human-friendly translatable title of the preference group to be used
  in menus and headings.

* **description** - Human friendly translatable description of the preference group
  to be used in UI.

* **class** - A mixin class for the preference group. The ZCML directive creates
  a new class using ``zojax.preferences.preference.PreferenceGroup`` as base
  and mixing in custom class if given. It can be used to override behaviour
  or implement some custom methods.

* **provides** - A list of additional interfaces that the preference group will
  provide. Can be used to mark the preference group with marker interfaces,
  for example to give access to special browser views.

* **accesspermission** - An id of permission that will be used for accessing fields
  defined in schema for reading.

* **permission** - An id of permission that will be used for writing into fields
  defined in schema.

* **tests** - A list of global functions that will be used for testing whether the
  preference group is available. These functions should recieve one argument -
  the actual preference group.

* **order** - An order hint. The sub-groups will be sorted using this value, so
  you can control the order of preference groups for UI.

If you need more control over attribute access permissions for the preference
group, you can use "require" and "allow" sub-directives with the same sematics
as with standard zope "class" directive.

Full example:

    <zojax:preferenceGroup
      id="profile"
      for=".interfaces.IProfileAwarePrincipal"
      schema=".interfaces.IProfile"
      title="Profile"
      description="Personal profile information such as full name, age, etc."
      class=".profile.Profile"
      provides=".interfaces.ISomeMarker"
      accesspermission="zope.View"
      permission="zojax.ModifyPreference"
      tests=".profile.isProfileAvailable"
      order="1">

      <allow attribute="fullName" />

      <require
        permission="yourproject.ChangePassword"
        attributes="setPassword"
        />

    </zojax:preferenceGroup>


### Availability testing


The preference group objects have the ``isAvailable`` method, as described in
the IPreferenceGroup interface. It does checking whether the preference group is
available in current conditions, so it can be hidden in UI for example.

You can override this method in custom preference group class, but default
implementation is fine in most cases. The default implementation of this method
does check if the parent group available and then performs checking using "test"
functions (see "tests" argument of the ZCML directive) and if either of them
returns False value, the preference group won't be available.


### Custom browser views


The default browser UI for a preference group is an edit form for fields defined
in the group's schema, but you can override the view, simply registering own view
for the preference group schema interface.

This fact can be used if you want to create more complex preference group that,
for example, does not contain any fields, but provides some other methods of
changing principal-related data, or if you just want to place a special form
in the user preferences tree in the UI.


### Preference data storage


The default preference group implementation (the ``zojax.preferences.preference.PreferenceGroup``
class) has the ``data`` property that is a per-principal persistent object where
values of preference group fields are stored as simple attributes.

That object is available via adapter lookup from (principal, preferencegroup)
pair to the ``zojax.preferences.interfaces.IDataStorage`` interface.

The default adapter regitered uses principal annotation mechanism to store
per-principal data (see ``zojax.preferences.storage``), however you can provide
your own adapter for specific types of principals and/or preference groups.

Here's a simple example of a custom data storage for a special type of
principals and special type of preference group - profiles (we used them
in the full ZCML directive example):

    class DataStorage(Persistent):
       implements(IDataStorage)

    @implementer(IDataStorage)
    @adapter(IProfileAwarePrincipal, IProfile)
    def getDataStorage(principal, preference):
        store = root['profiles'] # some mapping where preferences can be stored
        data = store.get(principal.id)
        if data is None:
            data = store[principal.id] = DataStorage()
        return data

Register it just like any other adapter:

    <adapter factory=".getDataStorage" />
