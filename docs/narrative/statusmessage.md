# Status messages


The ``zojax.statusmessage`` package provides functionality of creating short-lived
status (or "flash") messages used for notifying users about miscellanous status
changes, like form submitting results, logging in, etc.


## Basic usage


This section describes the very basics of this package - adding and displaying
messages.


### Adding messages


To add a simple status message, you need to adapt your request object to the
``zojax.statusmessage.interfaces.IStatusMessage`` interface and use its ``add``
method:

    IStatusMessage(request).add("Hello, World!")

This will add simple information message to the storage. The default implementation
uses sessions to separately store messages per client.

In the example above we added a message of default "info" type. But there's
two more message types available: "warning" and "error" which are rendered
differently, so you can differentiate message severities and meanings. To add
a message of other type, you need to specify its type name as second argument
of the ``add`` method:

    IStatusMessage(request).add("Something bad happened!", "error")
    IStatusMessage(request).add("This message will explore in 5 seconds!", "warning")


### Displaying messages


The default zojax skin does status message rendering in its "viewspace" layout,
but if you have own layout and want status message support for it, you need
to use the content provider named "statusMessage". Example:

    <div tal:content="structure provider:statusMessage" />


## Advanced usage


This section describes more advanced features and usage provided by this package.


### Custom message types


The message types, we talked about in the "Adding messages" section are pluggable
and are implemented as named adapters from request to the ``zojax.statusmessage.interfaces.IMessage``
interface. So those "info", "warning" and "error" type names are actually names
of message adapters provided by default.

Overriding existing message adapters or providing new ones is very easy, you
need to create an adapter class providing the "render" method and register it
as named adapter. The useful base class is provided in the ``zojax.statusmessage.message``
module, called "Message". Subclassing it, you only need to provide the rendering
code, the adapts/implements declarations and constructor is provided by this
base class. Example:

    from zojax.statusmessage.message import Message

    class CustomMessage(Message):

        def render(self, message):
            return u'<p class="custom">%s</p>' % message

Register it using the "adapter" ZCML directive:

    <adapter
        factory=".CustomMessage"
        name="custom"
        />

After registering you can specify "custom" as message type argument to the ``add``
method of ``IStatusMessage``:

    IStatusMessage(request).add("This is custom message", "custom")

Another useful base class is the ``InformationMessage``, in the same module. It
is a base class for all default implementations and does rendering of a message
in a `DIV` element with customizable `class` attribute. When subclassing
``InformationMessage``, you only need to provide own css class via ``cssClass``
class attribute. Example:

    from zojax.statusmessage.message import InformationMessage

    class CustomMessage2(InformationMessage):
        cssClass = 'custom'


### Custom message storage


The default implementation uses sessions for storing messages. If you are not
satisfied with this mechanism, you can provide own message storage system. To
do that, you need to create and register unnamed adapter from `request` to the
``zojax.statusmessage.interfaces.IStatusMessage`` interface. This interface
declares several methods that should be provided by message storage adapter.
The following example implements all required methods:

    from zope.component import adapts, getAdapter
    from zope.interface import implements
    from zope.publisher.interfaces import IBrowserRequest

    from zojax.statusmessage.interfaces import IStatusMessage, IMessage

    class CustomStatusMessage(object):
        adapts(IBrowserRequest)
        implements(IStatusMessage)

        def __init__(self, request):
            self.request = request
            self.storage = CustomStorage(request) # some custom per-request storage object

        def add(self, text, type='info'):
            message = getAdapter(self.request, IMessage, type)
            self.storage.append(message.render(text))

        def clear(self):
            return self.storage.return_and_clear()

        def messages(self):
            return tuple(self.storage)

        def __nonzero__(self):
            return bool(self.storage)
