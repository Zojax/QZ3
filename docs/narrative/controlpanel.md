# Control panel


The [zojax.controlpanel](https://github.com/Zojax/zojax.controlpanel/tree/master/src/zojax/controlpanel)
package provides an easy way to add per-site configuration snippets (we'll call
them `configlets`), automatically handling data storage and browser UI.

For those who knows [zojax.preferences](https://github.com/Zojax/zojax.preferences/tree/master/src/zojax/preferences),
this package work in a similar way, but storing data per site instead of per principal.


## Basic usage


In most simple cases, when you just want to store some configuration for a site,
creating a configlet is easy. First, you need to create a schema for a configlet,
defining fields that will be stored. Example:

    class ISiteMetaData(Interface):

        keywords = TextLine(title=u'Keywords', required=False)
        description = Text(title=u'Description', required=False)

And second, you need to register a configlet for this schema using the
``zojax:configlet`` ZCML directive:

    <zojax:configlet
        name="metadata"
        schema=".interfaces.ISiteMetaData"
        title="Site meta-data"
        />

The ZCML directive have three required arguments: **name**, **schema** and **title**.
``schema`` should point to a schema we create for a configlet, ``title`` is
a human-readable, translatable title for use in UI, and the ``name`` is an
unique identifier of a configlet.

Configlets are organized hierarchically, so one configlet can have children
configlets. In the ``name`` argument of the ZCML directive dot symbol has a
special meaning, used to declare hierarchies.

In the example above, we don't have any dots in the name. It means that this
configlet is a top-level one, it will be added to the root configlet. However, if we
create another configlet with, for example, "metadata.language" as its name,
the new configlet will be added as a child to our "metadata" configlet and it's
menu item will be rendered as a sub-menu item under the "Site meta-data".

There is no restriction on the depth of configlet nesting, but remember
that you should always register parent configlet before registering children.

After registering a configlet, it will be available as named IConfiglet utility,
with name equal to the value of ``name`` argument of the ZCML directive.

**Note:**

> The configlet objects are not persistent and only those attributes will be
   stored by default that are defined in the configlet schema.

The browser UI for the control panel (which is a collection of configlets) is
available as view named "settings" for the site objects (objects providing
``zope.app.component.interfaces.ISite`` interface). So if your site root is at
"http://yoursiteurl.com", the control panel will be available at
"http://yoursiteurl.com/settings".


## Advanced usage


### ZCML directive


The ``zojax:configlet`` ZCML directive has more arguments that can be used to
make a more specific configlet. Let's describe them all:

* **name** - The unique identifier of a configlet. Hierarchy of configlets is
  organized using dots in the names (see above).

* **schema** - Configlet schema interface. By default, storable properties will be
  created only for fields defined in this schema. It makes sense to use an
  empty interface as the schema, in case you want the configlet to be
  registered and provide custom data storage mechanism and/or browser views.

* **title** - Human-friendly translatable title of a configlet to be used in menus
  and headings.

* **description** - Human friendly translatable description of a configlet to be
  used in UI.

* **class** - A mixin class for the configlet. The ZCML directive creates a new
  class using ``zojax.controlpanel.configlet.Configlet`` as base and mixing
  in custom class if given. It can be used to override behaviour or implement
  some custom methods.

* **provides** - A list of additional interfaces that the configlet will provide.
  Can be used to mark a configlet with marker interfaces, for example to give
  access to special browser views.

* **permission** - An id of permission that will be used for accessing fields defined
  in the schema for reading and writing. By default, ``zojax.Configure`` is used.

* **tests** - A list of global functions that will be used for testing whether the
  configlet is available. These functions should recieve one argument - the
  actual configlet object.


If you need more control over attribute access permissions for the configlet,
you can use "require" and "allow" sub-directives with the same sematics
as with standard zope "class" directive.

Full example:

    <zojax:configlet
      name="siteinfo"
      schema=".interfaces.ISiteInfo"
      title="Site information"
      description="Misc site information, such as title, main author etc."
      class=".configlet.SiteInfoConfiglet"
      provides=".interfaces.ISomeMarker"
      permission="zojax.ChangeSiteInfo"
      tests=".configlet.isSiteInfoAvailable">

      <allow attributes="title" />

      <require
        permission="yourproject.ChangeMainAuthor"
        set_attributes="mainAuthor"
        />

    </zojax:configlet>


### Availability testing


Configlet objects have the ``isAvailable`` method, as described in the IConfiglet
interface. It does checking whether the configlet is available in current
conditions, so it can be hidden in UI for example.

You can override this method in custom configlet class, but default implementation
is fine in most cases. The default implementation of this method does check if
the parent configlet available and then performs checking using "test" functions
(see "tests" argument of the ZCML directive) and if either of them returns False
value, the configlet group won't be available.


### Custom browser views


The default browser UI for a configlet is an edit form for fields defined in its
schema, but you can override the view, simply registering own view for the
configlet schema interface.

This fact can be used if you want to create more complex configlets that,
for example, does not contain any fields, but provides some other methods of
changing site-related data, or if you just want to place a special form in the
site control panel UI.


### Configlet data storage


The default configlet implementation (the ``zojax.controlpanel.configlet.Configlet``
class) has the ``data`` property that is a per-site persistent data object where
values of configlet fields are stored.

That object is available via adapter lookup from configlet to the
``zojax.controlpanel.interfaces.IConfigletData`` interface and can have different
nature for different configlet types. However, the default implementation of
configlet field properties (that are created for every field in configlet's schema)
assumes that this object has mapping interface for storing values. So does the
default IConfigletData adapter implementation.

The default IConfigletData adapter is quite complex and customizable, so let's
talk some more about it.

First, this adapter uses the special IConfigletDataFactory interface to actually
create IConfigletData object, so if you just want to provide custom data
object and don't want to think about how it will be stored, you can simply
provide an adapter from your configlet type to the IConfigletDataFactory
interface, which is a simple callable factory that should return the
IConfigletData object.

And second, it also uses the IConfigletDataStorage adapter lookup to get the
persistent mapping object where configlet data objects will be stored by their
configlets' unique names. So, if you don't care about exact configlet data
object types and want to change their storage, you need to provide an adapter
from a site-manager (the object returned by site's ``getSiteManager`` method)
to the IConfigletDataStorage interface. The returned object should provide
mapping interface. The default adapter is provided for zope local site-managers
and stores a persistent container named "controlpanel" in the site-manager itself.
