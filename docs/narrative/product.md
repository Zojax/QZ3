# Products


The ``zojax.product`` package provides an easy way to create "product" packages
(a.k.a. plugins) for zojax. It maintains a product registry and provides browser
UI for managing products.

To the system, products are service objects that handles install, update and
uninstall process of some piece of plug-in software. They can be installed
per site.


## Basic usage


The most common type of products are registry-based products. In this case, you
register your components in a separate registry and the product adds or removes
that component registry to the site. The ``zojax:product`` ZCML directive
handles it perfectly.

To define a product, first, you need to create an interface for it. The product
system is also a part of control panel: products are registered as control panel
configlets and can have own per-site product configuration. Therefore, the
interface you create should also be a configuration schema for the product. If
your product has nothing to configure, simply provide an interface without any
schema fields. Example:

    class IMyProduct(Interface):
        """an interface for my product"""

Next, you need to actually create and register the product using ``zojax:product``
ZCML directive:

    <zojax:product
      name="myproduct"
      schema=".interfaces.IMyProduct"
      title="My Product"
      />

This directive is a lot like ``zojax:configlet`` so it has same three required
arguments: ``name``, ``schema`` and ``title``. Name is the unique product name,
schema is the product's interface and configuration schema. Title is translatable
human-readable product's title.

**Note:**

>  The product's configlet is registered as a child of a product configiration
  configlet named "products", so, if product's name is "myproduct", the name of
  its configlet will be "products.myproduct". See control panel documentation
  for more details on configlet hierarchy.

After this directive, the product's component registry will be created and made
available to be accessed via several ways:

* in the global ``registries`` object, which is name->product mapping, available
  in ``zojax.product`` module, so the registry of a product named "myproduct" will
  be available as "zojax.product.registries['myproduct']".

* as an object in the ``zojax.product`` module named after the product name, so
  the registry of a product named "myproduct" will be available as
  "zojax.product.myproduct".

* as the global ``zope.component.interfaces.IComponents`` utility named after the
  product's name.

After the product has been defined, you can wrap your product's component
registration in the ``registerIn`` ZCML directive. For example:

    <registerIn registry="zojax.product.myproduct">
      <adapter factory=".some.SomeAdapter" />
      <include package=".browser" />
    </registerIn>

So any component registrations specified in the "registerIn" directive will be
done in a product registry instead of global one.

The product itself will be available as a ``zojax.product.interfaces.IProduct``
utility named after the product name or as an unnamed utility with interface
specified in the ``schema`` argument of the ZCML directive.

In the UI, the product will be available to install/uninstall in portal's control
panel, in the "Products management" section. If your product's schema has
some fields and you want them to be editable through product configuration form
by default, you need to specify the ``configurable`` argument to the ZCML
directive as "true":

    <zojax:product
      name="myproduct"
      schema=".interfaces.IMyProduct"
      title="My Product"
      configurable="true"
      />

When product is set to "configurable", a configlet for editing its schema's
fields appears under the "Products management" in the control panel menu,
titled after product's title.

**Note:**

>  The "configurable" option only controls the availability of product's
  configlet in the control panel. The properties for storing product schema's
  fields will be created and available in any case.


## Advanced usage


This section describes advanced topics of zojax product system, including
custom installation logic and product dependencies.


### "zojax:product" ZCML directive


The "zojax:product" directive inherits from "zojax:configlet" provided by the
``zojax.controlpanel`` package, so most of its arguments are the same, as
products are reall a special case of configlets. We will briefly describe common
arguments here, and how they differ between two directives, for more information,
please also read control panel narrative documentation.

* **name** - Unique name for the product. The product will be registered as a named
  utility with this name. Unlike "name" argument of "zojax:configlet" directive,
  this argument's value should not contain dots. Also note, that the product's
  configlet will be registered with "products." prefix (e.g. "products.myproduct").

* **schema** - Product's main interface and configuration schema. Per-site data
  properties will be created for fields defined in this schema and the product
  will be also registered as an unnamed utility providing this interface.

* **title** - Human-readable translatable title for use in UI.

* **description** - Human-readable translatable description for use in UI.

* **class** - Mixin class for the product. Can override product's and/or configlet's
  methods to provide additional logic.

* **provides** - List of additional interfaces that the product will be marked as
  providing.

* **permission** - ID of a default permission used access the product. By default,
  ``zojax.ManageProducts`` is used.

* **tests** - List of functions or other callable objects that will be used to check
  whether the product's configlet available for UI.

* **configurable** - Boolean value defining whether product's schema can be edited
  using product's configuration form.

* **require** - List of product names that should be installed/updated before this
  one is installed or updated. This argument is used to define product
  dependencies.

If you need more control over product attribute access permissions, you can
use "require" and "allow" sub-directives with the same sematics as with standard
zope "class" directive.

Full example:

    <zojax:product
      name="myproduct"
      schema=".interfaces.IMyProduct"
      title="My Product"
      description="Some example product"
      class=".product.MyProduct"
      provides=".interfaces.ISomeMarker"
      permission="myproduct.ManageMyProduct"
      tests=".product.isMyProductAvailable"
      configurable="true"
      require="myotherproduct anotherproduct">

      <allow attributes="title" />

      <require
        permission="myproduct.ChangeSecret"
        set_attributes="secret"
        />

    </zojax:product>


### Product dependencies


zojax products support simple inter-product dependencies. One product can
"require" other products. Required products will be installed and updated
automatically BEFORE the requiring product installation/update.

It's developer duty to prevent circular requirements or infinite recursion
will occur.


### Additional product/configlet logic


You can provide a mix-in class in the "class" argument of ``zojax:product`` ZCML
directive. In this class you can override methods related to product as well
as ones related to configlet.

Product methods that are quite interesting are:

* **install** - called on product installation when product is not already installed.
* **update** - called when product is installed, but needs to be updated.
* **uninstall** - called when product is uninstalled.

Default implementations does quite a lot of work, including component registry
handling and event firing, so if you want to add additional logic, you'd better
call superclass methods before.

Also note, that the default "install" method class "update" in the end, so if
you need to provide common install/update additional code, simply add it to
the "update" method.

The other way of providing the custom install/update logic is to provide a
``z3c.configurator`` plugin for the product. Example:

    from z3c.configurator import ConfigurationPluginBase

    class MyProductConfiguration(ConfigurationPluginBase):

        def __call__(self, data=None):
            # the product object is available as self.context
            pass

Register it as a named adapter to your product:

    <adapter
      for=".interfaces.IMyProduct"
      provides="z3c.configurator.interfaces.IConfigurationPlugin"
      name="myproduct.config"
      />


### Product events


As said in previous chapter, default product implementation does fire events
on install/update/uninstall. They can be used to add even more logic to be
processed after product (un)installation.

There are three event interfaces defined in ``zojax.product.interfaces``:

* IProductInstalledEvent - product installed
* IProductUninstalledEvent - product uninstalled
* IProductUpdatedEvent - product updated

Every one of them has two attributes: ``id`` and ``product``. id is the product
name and product is the product object itself.

Note, that with default implementation, ``IProductUpdatedEvent`` will be fired
after first-time product installation as well.
