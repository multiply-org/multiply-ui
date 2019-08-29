var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');

var LabeledCheckboxView = widgets.DOMWidgetView.extend({

    render: function() {
        this.label = document.createElement('label');
        this.el.appendChild(this.label);
        this.label.className = 'widget-label';
        this.label.style.display = 'none';

        this.listenTo(this.model, 'change:description', this.updateDescription);
        this.listenTo(this.model, 'change:description_tooltip', this.updateDescription);
        this.el.classList.add('jupyter-widgets');
        this.el.classList.add('widget-inline-hbox');
        this.el.classList.add('widget-checkbox');

        // adding a zero-width space to the label to help
        // the browser set the baseline correctly
        this.label.innerHTML = '&#8203;';

        // label containing the checkbox and description span
        this.checkboxLabel = document.createElement('label');
        this.checkboxLabel.classList.add('widget-label-basic');
        this.el.appendChild(this.checkboxLabel);

        // checkbox
        this.checkbox = document.createElement('input');
        this.checkbox.setAttribute('type', 'checkbox');
        this.checkboxLabel.appendChild(this.checkbox);

        // span to the right of the checkbox that will render the description
        this.descriptionSpan = document.createElement('span');
        this.checkboxLabel.appendChild(this.descriptionSpan);

        this.value_changed();
        this.update_color();
        this.font_weight_changed();

        // Python -> JavaScript update
        this.model.on('change:value', this.value_changed, this);
        this.model.on('change:color', this.update_color, this);
        this.model.on('change:font_weight', this.font_weight_changed, this);
        this.model.on('change:disabled', this.disabled_changed, this);
        // JavaScript -> Python update
        this.checkbox.onchange = this.input_changed.bind(this);

        this.listenTo(this.model, 'change:indent', this.updateIndent);


        this.updateDescription();
        this.disabled_changed();
        this.updateIndent();
    },

    value_changed: function() {
        this.checkbox.checked = this.model.get('value');
    },

    update_color: function() {
        this.checkboxLabel.style.color = this.model.get('color');
    },

    font_weight_changed: function() {
        this.checkboxLabel.style.fontWeight = this.model.get('font_weight');
    },

    disabled_changed: function() {
        disabled = this.model.get('disabled');
        if (disabled) {
            this.checkboxLabel.style.color = "grey";
        } else {
            this.update_color();
        }
        this.checkbox.disabled = disabled;
    },

    input_changed: function() {
        this.model.set('value', this.checkbox.checked);
        this.model.save_changes();
    },

    updateDescription: function() {
        // can be called before the view is fully initialized
        if (this.checkboxLabel == null) {
            return;
        }
        description = this.model.get('description');
        this.descriptionSpan.innerHTML = description;
//        this.typeset(this.descriptionSpan);
        this.descriptionSpan.title = description;
        this.checkbox.title = description;
        this.checkbox.setAttribute('value', description);
    },

    updateIndent: function() {
        indent = this.model.get('indent');
        this.label.style.display = indent ? '' : 'none';
    },

});


module.exports = {
    LabeledCheckboxView : LabeledCheckboxView
};
