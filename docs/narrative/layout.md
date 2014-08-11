# Browser layout and page system


The ``zojax.layout`` package implements a flexible way to create browser pages
with higly customizable layouts and dipsplay logic.

This package registers browser pages as (context, request) adapters, so they
are simple views in a zope world. But the pages created by this package are very
smart. The main feature is extremely powerful content/layout separation mechanism,
including support for multiple layouts for different types of content, views and
skins, nested layouts, pluggable templates etc.

In the following chapters, we well use two main terms:

* **pagelet** - the "content" part of a browser page.
* **layout** - the layout in which pagelet is rendered.


## Basic usage


This chapter will show you how to create a page from template, class or both,
and how to define a layout for them.

Note, that we will use ZCML directives in the "zojax" namespace, to make them
available, you need to define that namespace pointing to "http://namespaces.zope.org/zojax"
in your ``configure.zcml`` file. Example:

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:zojax="http://namespaces.zope.org/zojax"
        >

      ... some directives in the "zojax" namespace"

    </configure>


### Creating pages


As said above, the page consist of the "pagelet" and "layout", in this chapter
we will talk about creating pagelets. To create a pagelet, we use the
``zojax:pagelet`` ZCML directive.


#### Providing only a template


One of the simplest cases is when you want to create a templated page for a
content type, let's show how it's done:

    <zojax:pagelet
      for=".interfaces.IContent"
      name="index.html"
      template="content.pt"
      />

In the example above, we created a pagelet named "index.html" for objects
providing "IContent" interface using template in the "content.pt" file. Note,
that did not specify access permission for this pagelet, that means that this
pagelet is public, so it will be accessible without restrictions.

When accessed, this pagelet will be rendered using default unnamed layout, or
if layout can not be found, it will be rendered without any layout. We'll
talk about layouts a bit later.

The template variables available in pagelet's templates are the same as with
standard zope view templates (using ``ViewPageTemplateFile`` class from the
``zope.app.pagetemplate`` package):

* ``context`` - the context object
* ``request`` - the request object
* ``view`` - the view object that uses this template
* ``template`` - the template object (for accessing macros for example)
* ``nothing`` - the None object


#### Providing a template and a class


If you want to provide some logic in the pagelet, such as getting needed values
or processing some request arguments, you can provide a mix-in class. QZ3
pagelet system uses the update/render pattern, so pagelet classes have the
"update" method that performs required actions, and the "render" method that
does the rendering of pagelet.

The default "render" method does rendering of the pagelet's template and the
default "update" method does nothing. So, if we want to use a template, but
include some logic before template is rendered, we need to provide own "update"
method.

Let's create a "smart" helloworld-type pagelet class:

    class GreeterPage(object):

        def update(self):
            self.who = self.request.get('who', 'World')

As you can see, it sets the "who" attribute to itself, getting the data from
the request. From a template, it can be accessed via "view" variable:

    <p>
      Hello, <span tal:replace="view/who" />!
    </p>

Finally, register the pagelet with ZCML directive, passing the mix-in class
as the "class" argument:

    <zojax:pagelet
      for="*"
      name="hello.html"
      template="hello.pt"
      class=".GreeterPage"
      />

Note that in the example above we used asterisk ("*" sign) in "for" argument,
that means that the pagelet is registered for any type of object.


#### Providing only a class


There is two cases when you want to only provide a class and don't provide any
template for a pagelet:

1. You want to implement custom rendering.
2. You want template to be provided separately, in other place or be dependent
   on a browser skin/layer.

zojax pagelets support both.

In a first case, you need to provide a class with custom "render" method that
should return a string ready to include in a layout.

Let's give an example of such class:

    class CustomRender(object):

        def render(self):
            return u'<p>Hello world!</p>'

This class doesn't need any templates, as it renders the ready-to-use HTML
content. It can be registered without specifying the "template" argument:

    <zojax:pagelet
      for="*"
      name="hello2.html"
      class=".CustomRenderPage"
      />


In the second case, when you want to provide template separately, you shouldn't
override the "default" render behaviour and shouldn't provide a template when
registering a pagelet.

Let's use for example a "smart" greeter view class we used above:

    class GreeterPage(object):

        def update(self):
            self.who = self.request.get('who', 'World')

But now, we'll register it without providing a template:

    <zojax:pagelet
      for="*"
      name="hello3.html"
      class=".GreeterPage"
      />

What the default "render" implementation will do is try to search an unnamed
pagelet for this pagelet and current request object.

So, to register a template for the pagelet above, we need to register a
templated pagelet passing this pagelet in the "for" argument, without specifying
a name:

    <zojax:pagelet
      for=".GreeterPage"
      template="hello.pt"
      />

As you may notice, this trick gives even more control of rendering, because you
can provide custom logic for that "template pagelet", giving another class via
"class" argument. This can be extremely useful when you want to provide additional
logic when rendering third-party pagelets in your skins.


### Creating layouts


This chapter describes the layouts mechanism and ways of defining layouts.

In the previous chapter we described how to create differently rendered pagelets.
But all pagelets, when accessed from a browser are renderd into some layout.

Every web site nowadays has common look and feel thru all its pages, so it makes
sense to define layout separately. Moreover, in complex web applications, some
parts has different "sub-layout" inside one common layout. This is greatly
supported by the ``zojax.layout`` package.


#### Basics


So, to define a layout, we use the another ZCML directive, named ``zojax:layout``.
By default, pagelets use unnamed layout, registered either for a pagelet, or
content object, or both.

What layout does is rendering a pagelet framed in some layout elements, so let's
create such template. The pagelet is available as "view" variable in the template,
so it can call its "render" method:

    <html>
     <head>
      <title>Example layout</head>
     </head>
     <body tal:content="structure view/render">
      Here comes the content...
     </body>
    </html>

Now let's register this template as a layout for our ``GreeterPage`` pagelet,
that we created in previous chapter:

    <zojax:layout
      view=".GreeterPage"
      template="layout.pt"
      />

If we want to provide another layout for the same pagelet, but for different
content type, we can register it specifying the "for" argument:

    <zojax:layout
      for=".interfaces.ISomeContentMarker"
      view=".GreeterPage"
      template="layout2.pt"
      />

So, everything besides objects providing ``ISomeContentMarker`` will use
"layout.pt" template and ``ISomeContentMarker`` objects will use "layout2.pt"
template for the ``GreeterPage`` pagelet.


#### Nested layouts


Very often we need to use several layouts for different pages that still have
some common parent layout. Here nested named layouts come to help.

In the previous section, we registered basic HTML structure as a layout for
our pagelet. But let's imagine, that that basic HTML structure is required
for all pages in our web portal, but one of pagelets, the ``GreeterPage`` needs
additional layout needed for its presentation. To implement that, first, let's
register our basic HTML structure as a layouts named "portal":

    <zojax:layout
      for="*"
      name="portal"
      template="layout.pt"
      />

That means exactly that for any object there's a layout named "portal" that uses
the "layout.pt" template.

Now, let's create a "sub-layout" template for our greeter page:

    <div class="greeter" tal:content="structure view/render">
      here comes content
    </div>

We register it for our ``GreeterPage`` just like we did it first time,
excepting that we specify additional argument - "layout" that is a name
to a parent layout:

    <zojax:layout
      view=".GreeterPage"
      template="greeter_layout.pt"
      layout="portal"
      />

So, now our greeter page will be rendered somewhat like this:

    <html>
     <head>
      <title>Example layout</head>
     </head>
     <body>
      <div class="greeter">
       <p>
        Hello, World!
       </p>
      </div>
     </body>
    </html>

The original pagelet template is rendered in its sub-layout which is rendered
in its parent layout. The depth of nesting is not restricted, so you can create
sub-sub-layouts and so on.

**Note:**

>  The ``zojax.layout`` package has some default layout configuration defined in
  its "configure.zcml" file. This configuration is used by the zojax default
  browser UI.

>  First, it defines a default unnamed layout with a template containing a
  "div" element that wraps the content of a pagelet.

>  Second, that unnamed layout has a parent layout named "viewspace" that also
  adds its own wrapper HTML elements.

>  Third, the "viewspace" layout has another parent layout named "workspace",
  that, again adds more wrapper HTML elements.

>  And finally, the "workspace" has the "portal" layout as its parent that
  wraps the content with some HTML elements and renders status messages above.

>  The "portal" layout uses the zope3 "standard_macros" concept to render itself,
  so it will work with skins like "Rotterdam" or "Boston" from zope3. But if
  you are not planning to integrate zojax pagelets with those skins, you can
  simply override the "portal" layout for your skin.

>  The power in this is that you can override layout at any level for any pagelet
  or content object, adding your own page elements or changing existing ones.


#### Layout template variables


In addition to standard view template variables (context, request, view,
template, nothing), layout templates has additional variables:

* ``layout`` - the layout object which is similar to "view objects", but used for
  layouts. The custom view objects are described in the "Advanced usage" part
  of this document.

* ``mainview`` - the original pagelet that is requested the layout. In case of
  nested layouts, the "view" variable points to a sub-layout, so if you want to
  access the real pagelet, use this variable.


## Advanced usage


### ZCML directives


In this section, we will fully describe the ZCML directives provided by this
package.


#### "zojax:pagelet"


This directive is a lot like zope's ``browser:page`` directive, because their
functions are similar.

* **for** - An interface or class this pagelet is registered for. For special cases,
  when you want to register a pagelet for several contexts, you can specify
  multiple interfaces/classes here, separated by a space.

* **name** - Pagelet's name. Browser pages (which pagelets are) are looked up as
  named adapters for context and request, so this is the adapter's name.

* **permission** - ID of a permission to be used to protect this pagelet.

* **allowed_interface** - Space-separated list of interfaces that defines pagelet's
  attributes to be allowed for usage using permission specified in the "permission"
  argument.

* **allowed_attributes** - Space separated list of names of attributes to be allowed
  for usage using permission specified in the "permission" argument.

* **layer** - Request layer interface in which this pagelet will be available.

* **class** - A mixin class to be used for creating custom pagelet class.

* **template** - Path to a file with template that this pagelet will use.

* **layout** - Name of the layout to be used by this pagelet for rendering itself
  when called directly. By default pagelets use unnamed layout.

* **type** - Space-separated list of pagelet types. Pagelet type is a named interface
  which pagelets can provide and will be registered providing, so you can query
  the pagelet using the "type" interface as required one for adapter lookup.
  This argument's values can be either names of pagelet types or pointings to
  actual interfaces. Pagelet types are registered using ``zojax:pageletType``
  ZCML directive described below.

* **provides** - Space-separated list of additional interfaces that this pagelet
  will provide. This can be used for example for marking a pagelet with a
  special marker interface to make it support its own views or other adapters.
  If some of these interfaces are "pagelet type" interfaces, the pagelet will
  also be registered as adapter providing these interfaces.

Any additional arguments specified in the directive will be set as string
attributes of pagelet's class. This is useful when you have some common pagelet
mixin class that uses its class arguments to define its look or behaviour (e.g.
some CSS class could be specified this way).


#### "zojax:pageletType"


This directive registers a pagelet type interface. See ``zojax:pagelet`` directive
description on for more info on pagelet types.

* **name** - Name of pagelet type.

* **interface** - Pagelet type interface. It will be registered as a named utility
  providing ``zojax.layout.interfaces.IPageletType`` using the name specified
  in directive's "name" argument.


#### "zojax:layout"


This directive creates and registers layout adapters for pagelets.

* **name** - Name which will be used to register layout. Pagelets and other layouts
  use this name to get a layout.

* **for** - Interface or class of a context object that this layout will be registered
  for. To register a layout, you MUST supply either this argument, or "view" or
  both.

* **view** - Interface or class of a pagelet that this laoyut will be registered
  for. This can point to a pagelet type interface. To register a layout, you
  MUST supply either this argument, or "for" or both.

* **layer** - Request layer interface in which this layout will be available.

* **template** - Path to a layout template file.

* **contentType** - Template content type in "<media>/<subtype>" form. This will
  be set as a "Content-Type" header when rendering a template, if none was
  supplied in the view.

* **layout** - Name of a parent layout in which this one will be rendered.

* **class** - Custom mixin class for the layout. Layout mixin classes are described
  further.

* **provides** - Interface that this layout will provide and be registered providing.
  If not specified, it is ``zojax.layout.interfaces.ILayout``.

* **title** - Human readable layout title for use in UI.

* **description** - Human readable layout description for use in UI.

* **uid** - Unique layout identifier. This argument is used if you want to provide
  special handling for some layouts. If it's specified, the ``zojax.layout.interfaces.ILayoutCreatedEvent``
  will be fired after layout registration and the event's "uid" attribute will
  be set to this value.

Any additional arguments specified for this directive will be set as string
attributes of a layout class created.


### Pagelet traverser


You can access any pagelet for any object in template using the "pagelet" or
"pageletObject" traverser views.

The "pagelet" view returns rendered pagelet content by its name. Example:

    <div tal:content="structure context/@@pagelet/view_fragment" />

This expression will look up pagelet named "view_fragment" for an object
available in the "context" variable and current request, update & render it
and return rendered content.

The "pageletObject" view returns a prepared pagelet object without rendering it.
Example:

    <div tal:define="fragment context/@@pageletObject/view_fragment">
      ... any usage of the "fragment" variable ...
    </div>

This expression will look up the same pagelet in a same way as in previous
example, but it will only update it without rendering and return the actual
pagelet object for further in-template processing. You can render it using the
"render" method:

    <tal:block replace="structure fragment/render" />


### "pagelet" TAL expression


Another way of rendering other pagelet in a template is using the "pagelet"
TAL expression. You simply need to specify pagelet's name and it will be
looked up and updated+rendered for current context and request:

    <div tal:content="structure pagelet:view_fragment" />


### Layout mixin classes


Layouts are actually a lot like pagelets as they are adapters that render
templates. They also follow update/render pattern to do the actual work.
So, if you need to add some logic to layout, you can give a mix-in class
that provides custom "update" method. This is done by specifing a class
in "class" argument of ``zojax:layout`` ZCML directive.

Like pagelets, layout objects have their ``context`` and ``request`` attributes,
and in addition, layouts have ``view`` attribute that points to the view that
this layout is for.


### Location-aware layout


Layout querying is context location-aware. That means that if no layout is found
for current context object, it will be looked up in its parents.
