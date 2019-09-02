var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');

var LabeledCheckboxView = widgets.DOMWidgetView.extend({

    render: function() {
        this.label = document.createElement('label');
        this.el.appendChild(this.label);
        this.label.className = 'widget-label';
        this.label.style.display = 'none';

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

        // Python -> JavaScript update
        this.listenTo(this.model, 'change:color', this.updateColor);
        this.listenTo(this.model, 'change:enabled', this.updateEnabled);
        this.listenTo(this.model, 'change:font_weight', this.updateFontWeight);
        this.listenTo(this.model, 'change:indent', this.updateIndent);
        this.listenTo(this.model, 'change:label_text', this.updateLabelText);
        this.listenTo(this.model, 'change:selected', this.updateSelected);
        this.listenTo(this.model, 'change:tooltip', this.updateTooltip);

        // JavaScript -> Python update
        this.checkbox.onchange = this.input_changed.bind(this);

        this.updateColor();
        this.updateFontWeight();
        this.updateLabelText();
        this.updateSelected();
        this.updateTooltip();
        this.updateEnabled();
        this.updateIndent();
    },

    input_changed: function() {
        this.model.set('selected', this.checkbox.checked);
        this.model.save_changes();
    },

    updateColor: function() {
        this.checkboxLabel.style.color = this.model.get('color');
    },

    updateEnabled: function() {
        disabled = !this.model.get('enabled');
        if (disabled) {
            this.checkboxLabel.style.color = "grey";
        } else {
            this.updateColor();
        }
        this.checkbox.disabled = disabled;
    },

    updateFontWeight: function() {
        this.checkboxLabel.style.fontWeight = this.model.get('font_weight');
    },

    updateIndent: function() {
        indent = this.model.get('indent');
        this.label.style.display = indent ? '' : 'none';
    },

    updateLabelText: function() {
        this.descriptionSpan.innerHTML = this.model.get('label_text');
    },

    updateSelected: function() {
        this.checkbox.checked = this.model.get('selected');
    },

    updateTooltip: function() {
        tooltip = this.model.get('tooltip')
        if (tooltip == null) {
          return;
        }
        this.descriptionSpan.title = tooltip;
        this.checkbox.title = this.model.get('tooltip');
   },

});


module.exports = {
    LabeledCheckboxView : LabeledCheckboxView
};
