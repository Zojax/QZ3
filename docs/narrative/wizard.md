# Wizards


The ``zojax.wizard`` package provides functionality for creating a special type
of browser pages - wizards. Wizard is a set of pages that are combined in a
sequence, user can move between these pages forward and back and availability
of each page can be dependent on some conditions. A page in this sequence is
called "step".

zojax wizard system is based on the ``z3c.form`` package and supports pluggable
steps and buttons. It can be used to define classic wizards which are a sequence
of steps where user goes one-by-one from first to last, as well as simple sets
of pages to combine them in one (for example, this technique is used for content
editing UI to provide pluggable content management pages under the single
management view).


## Basic usage


Wizards are a type of forms that support several standard buttons (like "next",
"previous", "save", "cancel", etc.), which can be customized. To define simple
wizard, you need to create a class inheriting ``zojax.wizard.wizard.Wizard``:

    from zojax.wizard.wizard import Wizard

    class MyWizard(Wizard):
        pass

And then register it using standard ``zojax:pagelet`` directive:

    <zojax:pagelet
        name="mywizard.html"
        for="*"
        class=".MyWizard"
        />

However, wizard won't be available until it has any steps. To add a step, create
its class, using ``zojax.wizard.step.WizardStep`` as a base:

    from zojax.wizard.step import WizardStep

    class MyWizardStep(WizardStep):
        pass

And register it as a named pagelet of type "wizard.step" for pair of content and
wizard using ``zojax:pagelet`` directive:

    <zojax:pagelet
        name="mystep"
        type="wizard.step"
        for="* .MyWizard"
        class=".MyWizardStep"
        weight="1"
        title="My Step"
        />

Note that we specified "weight" and "title" arguments as well. These arguments
are required for wizard steps. Weight is used for ordering steps in a wizard.

## Advanced usage

### Form steps

### Wizard with tabs
