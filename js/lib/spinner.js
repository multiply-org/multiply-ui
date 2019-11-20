var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');


var SpinnerView = widgets.DOMWidgetView.extend({

    render: function() {
        this.spinner_element = document.createElement("INPUT");
        this.spinner_element.setAttribute("type", "number");
        this.spinner_element.min = this.model.get('min');
        this.spinner_element.max = this.model.get('max');
        this.spinner_element.step = this.model.get('step');
        this.spinner_element.value = this.model.get('value');
        this.el.appendChild(this.spinner_element);
        // Python -> JavaScript update
        this.model.on('change:value', this.value_changed, this);
        // JavaScript -> Python update
        this.spinner_element.onchange = this.input_changed.bind(this);
    },

        value_changed: function() {
            this.spinner_element.value = this.model.get('value');
    },

        input_changed: function() {
            this.model.set('value', parseInt(this.spinner_element.value));
            this.model.save_changes();
    },

});

module.exports = {
    SpinnerView : SpinnerView
}
