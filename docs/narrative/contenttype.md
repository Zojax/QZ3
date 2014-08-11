# Content types


`QZ3` has its own content types system that allows to easily add new content
types, automatically creating its forms, add menu items, etc.

The package providing main content type creation features is ``zojax.content.type``.
It provides content types registration functionality, common base classes for
content types, including containers, ordering support for containers, etc.


## Basic usage


### Defining the content type


To create a content type, of course, we need to define its schema interface and
its class. It is strongly recommended to use the ``zojax.content.type.interfaces.IItem``
interface as base interface, because it defines "title" and "description" fields
that are used in many places of zojax system. Example:

    from zojax.content.type.interfaces import IItem

    class IDocument(IItem):

        body = Text(title=u'Body text', required=True)

The interface above actually defines three fields: **title**, **description**
and **body**. To provide an implementation, there is very handy content type base class -
``zojax.content.type.item.PersistentItem``. It implements the ``IItem`` interface,
supports ZODB persistency, containment (knows its parent and name), and is
annotatable (so it can support various content extensions). Example
implementation:

    from zojax.content.type.item import PersistentItem

    class Document(PersistentItem):
        implements(IDocument)

        body = None

The ``Document`` class can now be registered as zojax content type by using the
``zojax:contenttype`` ZCML directive:

    <zojax:contenttype
        name="yourmodule.document"
        title="Document"
        schema=".interfaces.IDocument"
        class=".Document"
        permission="yourmodule.AddDocument"
        />

This ZCML directive creates a special "content type" object, which contains
information about our content type and handles content object creation and
adding. It is available in several ways:

* As a ``zojax.content.type.interfaces.IContentType`` utility, named by the name
  specified in ZCML directive argument.

* As an adapter from the content class to the ``IContentType`` interface. This
  is useful if you want to get a content type object only having a content
  object.

* As an unnamed utility providing own interface, created especially for this
  content type. This interface is stored in the ``zojax.content`` module by name
  composed from the name specified in ZCML directive argument, replacing dots
  and hyphens with underscores. So, for example, an interface for our ``Document``
  content type will be available as ``zojax.content.yourmodule_document``.
  This is useful if you want to register some adapters or views for the content
  type object via ZCML.

  You can override this behaviour by providing your own interface for this use,
  see detailed ZCML directive description in the "Advanced Usage" section.


### Container types


Creating a new container content type is as easy as creating a simple content
type. There is a base class provided for containers -
``zojax.content.type.container.ContentContainer``. It has the same features as
the ``PersistentItem`` type, but also support object containment.

The content type interface could inherit from standard zope ``IContainer`` and
zojax ``IItem``:

    from zope.app.container.interfaces import IContainer
    from zojax.content.type.interfaces import IItem

    class IFolder(IItem, IContainer):
        """custom folder interface"""

The ``ContentContainer`` base class fully implements these interfaces:

    from zojax.content.type.container import ContentContainer

    class Folder(ContentContainer):
        implements(IFolder)

It is registered with ``zojax:contenttype`` ZCML directive just like any other
content type:

    <zojax:contenttype
        name="yourmodule.folder"
        title="Folder"
        schema=".interfaces.IFolder"
        class=".Folder"
        permission="yourmodule.AddFolder"
        />


### Creating content


So, what can we do with the content type object? First, it can be used for
creating actual content objects. This is done using the ``create`` method:

    from zojax.content.type.interfaces import IContentType

    ct = getUtility(IContentType, name='yourmodule.document')
    obj = ct.create(
      title=u'My TODO',
      description=u'Things i would like to do soon',
      body=u'1. Finish this document\n'
           u'2. Get paid'
      )

As you can see, we passed attribute values to the ``create`` method. It is quite
smart, as it handles constructor arguments (positional and keywords), passing
given arguments to it, and if some of keyword arguments are not handled by the
class constructor, they are used to set attribute values for fields defined
by a content type schema.

In case of our example ``Document`` content class, the "title" and "description"
values will be passed to the constructor, because the ``PersistentItem`` base
class handles them, and the "body" value will be set as a field value, after
object creation, because ``IDocument`` defines the "body" field.

The last thing done by the ``create`` method is firing the ``ObjectCreatedEvent``
for newly created object, so you don't need to do it yourself.


### Adding content


The second purpose content type objects are used for is adding content to
containers. To add a created content object to some container, first, we need
to "bind" a content type to the container. This is done by using the ``__bind__``
method:

    bound = ct.__bind__(container)

This method returns a bound clone of a content type object that knows about the
container we're going to add our objects to. Now, to add an object to a container,
we use the ``add`` method:

    bound.add(obj)

This simple call does the required security and constraint checks and adds an
object to the current container. It also automatically chooses a name for an
object using standard ``INameChooser`` mechanism provided by zope containers,
but if you want to specify your own name for added object, you can pass it as
second argument for the ``add`` method:

   bound.add(obj, 'main_todo')

Name chooser, constraints and addability checkers are described in advaced
sections of this document.


## Advanced usage


### zojax:contenttype ZCML directive


The ``zojax:contenttype`` directive has more features than described in the
basic usage section. Here are all the arguments that it supports:

* **name** - Unique name for a content type. It is used for component registrations
  and accessing a content type from ZCML using ``zojax.content`` module.

* **schema** - Main interface of a content type. Fields in this schema are used for
  automatically generating add and edit forms, as well as for setting attribute
  values in the ``create`` method of the content type object.

* **class** - Actual class, representing a content type. It should implement the
  interface specified in the ``schema`` argument.

* **title** - Human-readable, translatable title of a content type for use in UI.

* **description** - Human-readable, translatable description of a content type for
  use in UI.

* **permission** - Id of the permission required for adding an object of this type.

* **contenttype** - Custom interface to mark this content type with. Useful for
  registering additional adapters/views for a content type or group. Also, the
  content type object is registered as an unnamed utility providing this interface.
  If not specified, it will be created as an object in the ``zojax.content``
  module, named after the name specified in the ZCML directive, replacing dots
  and hyphens by underscores.

* **type** - Space-separated list of additional interfaces used to mark a content
  type object with. The content type object will be also registered as a named
  utility providing each of these interfaces using the name specified in the
  ZCML directive argument. There's several "type interfaces" provided, described
  later in this document.

* **contains** - Space separated list of content types that this content type can
  contain. This is used to add containment constraints for the container content
  types. Each value from this list can be either a name of a content type or an
  interface that is provided by it.

* **containers** - Space separated list of content types which this content type
  can be contained in. This is used to restrict content object's parent container
  types. Each value from this list can be either a name of a content type or an
  interface that is provided by it.

* **ctclass** - Custom class for the content type object. Used if you want to
  somehow override the default implementation.

* **addform** - The name of custom add form, registered for the
  ``zope.app.container.interfaces.IAdding``. By default, add forms are generated
  automatically for each content type, but if you want to provide your own, you
  should specify a name of add form view in this argument.


### "Content type" types

Types of a "content type" objects are special marker interfaces used to define
its nature. They are specified in the "type" argument of ``zojax:contenttype``
ZCML directive. There are serveral default types provided and used in other
parts of zojax. They are available in the ``zojax.content.type.interfacess``
module:

* **IActiveType** - Default type of any content type object. Means that the content
  type is available and should be included in displayed lists of content types.

* **IInactiveType** - Type that is used to mark that some content type should not
  explicitly added by the user, it won't be included in adding lists. When
  this type is specified, the ``IActiveType`` is removed from the list of types,
  so the content type can be only marked with one of them.

* **IPortalType** - Type that is used for mark content types that should be included
  in portal search forms.

* **IActivePortalType** - A combination of ``IActiveType`` and ``IPortalType``.

* **IExplicitlyAddable** - A marker type that means that this content type will
  show up in adding lists only if the container explicitly specifies it as a
  contained type.


### Container constraints

As described in the ``zojax:contenttype`` ZCML directive description, content
types can define their containment restrictions. Containers can restrict content
types that can be added to it and any content type can restrict containers that
this content type can be added to. This is normally done by "contains" and
"containers" ZCML directive arguments. This section describes how to check these
constraints.

Every content type objects has the ``listContainedTypes`` method that returns
an iterable of content type objects that can be contained in this content type.
Example:

    for contained_ct in ct.listContainedTypes():
        pass # contained_ct is a content type that is available for adding

This call returns an iterable of content types that can be added to an object
of this content type AND are available in current context (passes security and
other checks, see the next chapter). You can disable availability checking
by passing False as an argument to this method:

    for contained_ct in ct.listContainedTypes(False):
        pass # contained_ct is a content type that is registered as addable
             # to current content type, but it may not pass other availability
             # checks, like permission check, etc.

Also, every content type has the ``checkObject`` method that checks whether
given concrete object of this content type can be placed in a given container
under given name:

    ct.checkObject(container, 'some_name', obj)

Note, that this method does not return True or False, instead it raises a certain
exception in case of failure. These exceptions could be one of these:

* ``InvalidItemType`` - raised when given container cannot contain given object.
* ``InvalidContainerType`` - raised when given object cannot be contained in
  given container.

You can catch ``TypeError`` if you want to simply check the addability without
digging into actual potential problem.


### Availability checkers

Content type objects have ``isAddable`` and ``isAvailable`` methods uses to
check availability and addability of a content type in current bound container.
Default implementation uses the pluggable mechanism that allows to add
additional checks without providing custom content type class.

This is done by providing an adapter from a pair of content type object and
container object to the ``zojax.content.type.interfaces.IContentTypeChecker``
interface. This adapter is very simple - it should only provide the ``check``
method that returns whether the content type is available in this container.

Example:

    from zojax.content.type.interfaces import IContentTypeChecker

    class ExampleChecker(object):
        adapts(ISomeContentType, ISomeContainer)
        implements(IContentTypeChecker)

        def __init__(self, contenttype, container):
            self.contenttype = contenttype
            self.container = container

        def check(self):
            if len(self.container) >= 30:
                return False
            return True

The checker should be registered as a named adapter using the standard zope
``adapter`` ZCML directive:

    <adapter
        name="yourmodule.examplechecker"
        factory=".ExampleChecker"
        />

Of course, there can be any number of checkers provided per any content type
and/or container.


### Name chooser

The ``zope.app.container`` package contains an useful mechanism for choosing
and checking names for new objects. Zojax content types system provides an
extended version of name chooser.


#### Reserved names

One of the features of zojax name chooser is that it supports reserved names. For
example, you may want to reserve some names for views (so they won't be overriden
by contained items on URL traversing) or special child objects. The default
implementation is very simple: a list of reserved names are specifying using
the ``zojax:reservedNames`` ZCML directive:

    <zojax:reservedNames
        for=".interfaces.ISomeContainer"
        names="categories index"
        />

This will restrict adding objects under names "categories" and "index". If you
want more smart reserved names logic, you can provide an adapter for your
container implementing ``zojax.content.type.interfaces.IReservedNames`` interface,
which is simply define the "names" attribute which is a tuple of reserved names.
Let's provide an example of dynamic reserved names adapter:

    from zojax.content.type.interfaces import IReservedNames

    class ExampleReservedNames(object):
        adapts(ISomeContainer)
        implements(IReservedNames)

        def __init__(self, context):
            names = getReservedNames(context)  # getReservedNames is some function
                                               # that returns a sequence of names
            self.names = tuple(names)

It is registered as an unnamed adapter using zope ``adapter`` ZCML directive:

    <adapter factory=".ExampleReservedNames" />


#### Object-dependent name choosing

Default zope name chooser mechanism allows to define only one name chooser per
container, but in QZ3, you can provide several name choosers depending on type
of object that is being added to the container. To do that, you need to provide
an adapter from (container, object) pair to the ``INameChooser`` interface.

Example:

    from zope.app.container.contained import NameChooser

    class ExampleNameChooser(NameChooser):
        adapts(ISomeContainer, ISomeContent)

        def __init__(self, context, object):
            super(ExampleNameChooser, self).__init__(context)
            # note that we don't store the object, as it will be passed in
            # the `chooseName` method anyway.

        def chooseName(self, name, object):
            # ... choose a name and return it ...
            return name

This adapter should be registered for container and object using the ``adapter``
ZCML directive:

    <adapter
      for=".interfaces.ISomeContainer .interfaces.ISomeContent"
      factory=".ExampleNameChooser"
      />


#### Title-based name choosing

One of object-dependent name chooser provided is the title-based name chooser.
It is registered for objects providing ``zojax.content.type.interfaces.ITitleBasedName``
marker interfaces and chooses a name for a new object from its title.

This name chooser has some per-site configuration that can be changed by portal
manager. Check "Name chooser" configlet in the portal control panel.


### Order support

``zojax.content.type`` package provides item ordering support for any container
type. The ``zojax.content.type.interfaces.IOrder`` defines a read-only container
interface that returns items in an order. An order-aware container should be
adapted to this interface to get items in the correct order. So, for example to
list items in the ordered container, you write this:

    for name in IOrder(container):
        pass # do something

Pretty easy, isn't it? But note, that the adapter only works for containers that
are marked as order-aware. The default implementation uses annotations to store
order information, so your container should also be annotatable. To mark your
container as order-aware using annotations, you should use the
``zojax.content.type.interfaces.IAnnotatableOrder`` marker interface. Example:

    <class class=".SomeContainer">
      <implements interface="zojax.content.type.interfaces.IAnnotatableOrder" />
    </class>

In the default annotatable order implementation, newly added objects are added
to the end of the order.

Default ``IOrder`` adapter also provides other important interface -
``zojax.content.type.interfaces.IReorderable`` which defines methods to change
the order:

* moveUp - moves given sequence of item names up in the order
* moveDown - moves given sequence of item names down in the order
* moveTop - moves given sequence of item names to the top
* moveBottom - moves given sequence of item names to the bottom
* updateOrder - reorder items using given sequence of names; that sequence
  should contain all names that are contained in the container or this method
  will raise an exception.

Example:

    order = IOrder(container)
    if IReorderable.providedBy(order): # we can check if order supports modifying
        order.moveTop(('main-page', 'documents'))

## User interface

zojax content types system provides a bunch of default UI for managing content
objects, including add and edit forms, content listing and deletion views.


### Container contents

To enable the "Contents" view for a container, simply make it implement the
``zojax.content.type.interfaces.IContainerContentsAware`` interface. Example:

    <class class=".ExampleContainer">
      <implements interface="zojax.content.type.interfaces.IContainerContentsAware" />
    </class>


### Adding content

Content adding forms are accessed using a special "+" view for a container. This
view publishes content types when traversed further (e.g.
"http://path.to/your/container/+/yourmodule.document"). And the view for a
context type object is its add form, automatically generated by ``zojax.content.forms.form.AddForm``
class.

Earlier, we described one way of providing a custom add form by using the "addform"
argument to the ``zojax:contenttype`` directive. Other way is to override the view
named "index.html" for your concrete content type. If you just want to provide
a same form with small changes, use the ``zojax.content.forms.form.AddForm`` as
a base class for your form. Example:

    from zojax.content.forms.form import AddForm

    class CustomAddForm(AddForm):

        label = u'Custom Label'

By default, form gets its label from content type's title, but we override it.
Now register it with a ``broser:page`` ZCML directive, just like the default
form is registered:

    <browser:page
        name="index.html"
        for=".interfaces.IYourContentType"
        class=".CustomAddForm"
        permission="zope.View"
        />


### Managing content

Content editing, changing its settings, ownership, etc. is combined to a
flexible content edit wizard that is greatly customizable by using pluggable
"wizard steps". It is accessed by appending "context.html" to the URL of your
content object.

Content editing wizard steps are named pagelets with type "wizard.step" registered
for content and wizard pair. They must provide the ``zojax.wizard.interfaces.IWizardStep``
interface and there are two useful base classes provided by the ``zojax.wizard.step``
module - ``WizardStep`` (generic wizard step) and ``WizardStepForm`` (form step).

For example, you may want to override the default field editing form step, which
is registered as a "wizard.step" type pagelet named "content". To do this, first
create a custom pagelet class:

    from zojax.wizard.step import WizardFormStep

    class CustomEditStep(WizardFormStep):

        def update(self):
            ct = IContentType(self.context)
            self.fields = Fields(ct.schema)
            super(CustomEditStep, self).update()

And then register it with the ``zojax:pagelet`` directive:

    <zojax:pagelet
       name="content"
       type="wizard.step"
       for="yourmodule.interfaces.IYourContent
            zojax.content.forms.interfaces.IEditContentWizard"
       class=".CustomEditStep"
       permission="zojax.ModifyContent"
       weight="100"
       />

Notice that we registered the pagelet for ``IYourContent`` and
``zojax.content.forms.interfaces.IEditContentWizard``. The second is an interface
of the content edit wizard we create steps for.

You can add and override any content edit steps this way. See [zojax.wizard](https://github.com/Zojax/zojax.wizard)
documentation for more details on wizard step creation.
