# Forms


The ``zojax.layoutform`` package provides advanced form classes based on the
well-known ``z3c.form`` package. In addition to ``z3c.form`` features,
``zojax.layoutform`` provides:

* Greatly customizable pagelet-based form UI using ``zojax.layout``.

* Status messages using ``zojax.statusmessage``.

* Rich form extending support (adapter-based lookup of field groups, sub-forms,
  additional forms and views).

Form classes provided by this package are extended versions of ``z3c.form``
classes. If you are not familiar with ``z3c.form``, please, read its
documentation before.

The ``zojax.layoutform`` module provides 4 generic form classes for use to
create forms for zojax:

* **PageletForm** - the most generic form class that can be used for any type of
  form. Other form classes inherit this, so be sure to read its description
  below.

* **PageletDisplayForm** - form for displaying values instead of editing them.

* **PageletAddForm** - common form for adding content.

* **PageletEditForm** - common form for editing content.


### PageletForm


This is a base class for all other forms in this package. It provides a generic
pagelet-based form without any default buttons. It also implements support for
sub-forms and field groups, but this feature will be described in a separate
section. In addition, this class supports form "label" and "description" that
will be rendered in UI. Let's provide an example of a form:

    from zojax.layoutform import PageletForm, Fields, button

    class ExampleForm(PageletForm):

        fields = Fields(ISomeSchema)
        label = u'Example Form'
        description = u'This form will allow you to enter fields from ISomeSchema.'

        @button.buttonAndHandler(u'Done', name='done')
        def handleDone(self, action):
            data, errors = self.extractData()
            if errors:
                IStatusMessage(self.request).add(
                    (self.formErrorsMessage,) + errors, 'formError')
            else:
                pass # do something

Notice, that we imported "Fields" and "button" from the ``zojax.layouform`` module.
While "button" is just a short-cut to the ``z3c.form.button`` module, the "Fields"
class is a modified version of ``z3c.form``'s Fields. It removes all proxies from
given fields to make sure they won't cause any problems. This is useful, when you
want to use, for example, persistent schema fields that are protected by security
proxy.

Also, we used ``zojax.statusmessage`` to indicate errors in this example.
``zojax.layoutform`` provides own message type for form errors, called "formError".
It has special message adding logic: you should pass a sequence instead of single
message in the ``IStatusMessage.add`` method. The first element should be a string,
containing main message (we used predefined string in ``PageletForm.formErrorsMessage``),
and the rest of the sequence should be ``z3c.form.interfaces.IErrorViewSnippet``
objects, as returned by form's ``extractData`` method. Also note, that widget-bound
error view snippets won't be rendered in resulting status message, as they are
rendered later next to their widget.

The ``PageletForm`` class provides several generic messages that are recommended
to be used in standard situations. They are available as ``PageletForm``'s class
variables:

* successMessage - "Data successfully updated" message.

* noChangesMessage - "No changes were applied" message.

* formErrorsMessage - "Please fix indicated errors" message.

Form are registered as usual pagelets using the ``zojax:pagelet`` ZCML directive:

    <zojax:pagelet
      for=".ISomeSchema"
      name="someform.html"
      class=".ExampleForm"
      />

See ``zojax.layout`` documentation for more detailed description of this directive.


### PageletDisplayForm


This form class is pretty the same as ``PageletForm``, except that it renders
widgets in display mode, so it's used for displaying field values instead of
editing them. Example is very simple:

    from zojax.layoutform import PageletDisplayForm, Fields

    class ExampleDisplayForm(PageletDisplayForm):

        fields = Fields(ISomeSchema)


### PageletAddForm


The ``PageletAddForm`` is handy base class for any types of content adding forms.
It contains the "add" button that handles field validation, calling add methods
and request redirection and the "cancel" button to redirect the user back. All
you need is to provide the ``create`` and ``add`` methods. Example:

    from zojax.layoutform import PageletAddForm, Fields

    class ExampleAddForm(PageletAddForm):

        fields = Fields(ISomeSchema)

        def create(self, data):
            # data argument is a dictionary containing validated and converted
            # values submitted using the form. all we need is to create an object
            # using this data and return it.
            return SomeObject(data)

        def add(self, obj):
            # obj argument is an object just created by the "create" method
            someStorage.add(obj)

By default, the "add" button redirects an user to the added object and the
"cancel" button redirects to the current context object that the form is for.
You can override this behaviour by providing own "nextURL" and "cancelURL"
methods, for example:

    class ExampleAddForm2(ExampleAddForm):

        def nextURL(self):
            obj = self._addedObject # added object is available in "_addedObject" attribute
            return absoluteURL(obj, self.request) + '/context'

        def cancelURL(self):
            return self.request.getApplicationURL()


### PageletEditForm


The ``PageletEditForm`` class is used for creating content edit forms. It has
the "save" button that does form validation and applies changes. For basic
usage you don't need to provide any additional methods, just define fields.
Example:

    from zojax.layoutform import PageletEditForm, Fields

    class ExampleEditForm(PageletEditForm):

        fields = Fields(ISomeSchema)

This form will apply changes to the context object it is registered for. You
can override the changes applying logic by overriding ``applyChanges`` method:

    class ExampleEditForm2(PageletEditForm):

        fields = Fields(ISomeSchema)

        def applyChanges(self, data):
            content = self.getContent() # override this method if you want object
                                        # other thant context to be edited.

            # ...apply changes using own logic...
            # data argument given to this method contains a dictionary with
            # validated and converted form values

            return True # the returned value converted to bool indicates whether
                        # there was any change applied or not. you can simply return
                        # a dictionary of changes returned by z3c.form.form.applyChanges

By default, the form doesn't redirect user anywhere on a successful submit, but
you can override this behaviour by providing the ``nextURL`` method:

    class ExampleEditForm3(PageletEditForm):

        fields = Fields(ISomeSchema)

        def nextURL(self):
            # returning empty string means no redirect and is default behaviour,
            # but we'll override it by returning the current URL, so the form will
            # redirect to itself.
            return self.request.getURL()


### Common action types


To make UI more consistent, there are custom styles provided for some of generic
actions: save, cancel and add. To make a button recieve its styles, you need
to mark it with one of these interfaces, contained in ``zojax.layouform.interfaces``:

* **ISaveAction** - for save buttons
* **ICancelAction** - for cancel buttons
* **IAddAction** - for add buttons

The easiest way to do that is pass the "provides" argument to the
``z3c.form.button.buttonAndhandler`` function. For example:

    class SomeForm(PageletEditForm):

        @button.buttonAndHandler(u'Save', provides=ISaveAction)
        def handleSave(self, action):
            pass # do something


### Field groups


zojax forms support field groups provided by ``z3c.form.group`` module in a
pluggable way. They are looked up dynamically using named adapter from
context, form and request object triple to the ``zojax.layoutform.interfaces.IPageletSubform``
interface. To define a field group, first, you need to make it's class implement this
interface. Example:

    from zope.interface import implements
    from z3c.form.group import Group
    from zojax.layoutform.interfaces import IPageletSubForm

    class ExampleGroup(Group):
        implements(IPageletSubForm)

        weight = 0 # weight hint for ordering groups in a parent form
        fields = Fields(ISomeSchema)

        def __init__(self, context, form, request):
            # the order of positional arguments in z3c.form's Group initializer
            # is different from one required by IPageletSubForm adapter lookup,
            # so change the order to fix this problem.
            super(ExampleGroup, self).__init__(context, request, form)

        def isAvailable(self):
            return True # group can be disabled depending on some conditions

        def postUpdate(self):
            pass # this method is called after parent form update

After that, you need to register it for your parent form using the "adapter"
ZCML directive:

    <adapter
      for="* .ExampleForm *"
      provides="zojax.layoutform.interfaces.IPageletSubForm"
      name="example.group"
      factory=".ExampleGroup"
      />

We register our field group for the ExampleForm, for any context and request
type.

The field group values are extracted in the parent form's ``extractData`` as if
these fields was outside the field group, so in the example above, `ISomeSchema`
fields we used for our field group will be available in parent form's extracted
data dictionary without any difference from other form fields defined in parent
form.


### Sub-forms


Sub-forms are also supported by zojax forms. They differ from field groups in
that they doesn't have any impact on parent form, as they have separate fields
which values are not used in parent form.

As field groups, sub-forms are looked up as named adapters from (context, form,
request) object triple to the ``IPageletSubform`` interface and to define a
sub-form, you need it to implement that interface. Sub-forms should also provide
the ``z3c.form.interfaces.ISubForm`` interface.

The ``PageletForm`` is NOT a good base class for a sub-forms as it itself
does much handling subform handling. So, for simple sub-forms there's another
base class provided - ``PageletBaseForm``, which handles the pagelet-based
rendering and nothing more. Let's provide an example of sub-form:

    from z3c.form.interfaces import ISubForm
    from zojax.layoutform.form import PageletBaseForm

    class ExampleSubForm(PageletBaseForm):
        implements(ISubForm, IPageletSubForm)

        weight = 10 # weight hint for ordering groups in a parent form
        fields = Fields(ISomeSchema)

        def __init__(self, context, form, request):
            super(ExampleSubForm, self).__init__(context, request)
            self.parentForm = self.__parent__ = parentForm

        def isAvailable(self):
            return True # group can be disabled depending on some conditions

        def postUpdate(self):
            # this method is called after parent form update
            # ... do some processing ...
            pass

This form is registered just like the field group, using the "adapter" ZCML
directive:

    <adapter
      for="* .ExampleForm *"
      provides="zojax.layoutform.interfaces.IPageletSubForm"
      name="example.subform"
      factory=".ExampleSubForm"
      />

**Note:**

>  There's a more complex sub-form base class provided for editing content, see
  ``zojax.layoutform.PageletEditSubForm``. It supports own actions, managed by
  the parent form and provides the "save" action, just like ``PageletEditForm``.


### Additional forms and other views


Sometimes there's a need to plug in some additional separate form or even
non-form pagelet to the existing form. This is supported by ``zojax.layoutform``.
Additional forms differ from sub-forms in that they are rendered in a separate
"form" tag and don't influence on each other.

To append a form or other pagelet to the form, you need to provide the ``IPageletSubForm``
adapter, just like with groups and sub-forms, but you need to make sure that
your form/view provides neither ``ISubForm`` nor ``IGroup``.

For example, let's add an additional non-form pagelet to our form. First, we
need to create the ``IPageletSubForm`` adapter. That also provides "update" and
"render" methods:

    class AdditionalView(object):

        weight = 10

        def __init__(self, context, form, request):
            self.context = context
            self.request = request
            self.parentForm = form

        def update(self):
            pass

        def render(self):
            return u'Rendered content'

        def isAvailable(self):
            return True

        def postUpdate(self):
            pass

After that, we register it with ``adapter`` directive just like a sub-form or
field group:

    <adapter
      for="* .ExampleForm *"
      provides="zojax.layoutform.interfaces.IPageletSubForm"
      name="example.view"
      factory=".AdditionalView"
      />


### Form template customization


