var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'multiply-widgets',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'multiply-widgets',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};

