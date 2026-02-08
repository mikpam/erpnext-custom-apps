frappe.listview_settings['AI Task Log'] = {
    add_fields: ['status', 'prompt', 'model', 'timestamp'],

    get_indicator: function(doc) {
        var colors = {
            'Pending':    [__('Pending'),    'orange', 'status,=,Pending'],
            'Processing': [__('Processing'), 'blue',   'status,=,Processing'],
            'Completed':  [__('Completed'),  'green',  'status,=,Completed'],
            'Failed':     [__('Failed'),     'red',    'status,=,Failed']
        };
        return colors[doc.status] || [__('Unknown'), 'grey'];
    },

    onload: function(listview) {
        listview.page.add_action_item(__('Retry Failed'), function() {
            var selected = listview.get_checked_items();
            var failed = selected.filter(function(d) { return d.status === 'Failed'; });

            if (!failed.length) {
                frappe.msgprint(__('Select at least one failed task to retry.'));
                return;
            }

            frappe.confirm(
                __('Retry {0} failed task(s)?', [failed.length]),
                function() {
                    frappe.call({
                        method: 'ai_task_log.ai_task_log.api.retry_failed_tasks',
                        args: { task_names: failed.map(function(d) { return d.name; }) },
                        freeze: true,
                        freeze_message: __('Retrying failed tasks...'),
                        callback: function(r) {
                            if (r.message) {
                                frappe.show_alert({
                                    message: __('{0} of {1} tasks retried', [r.message.success, r.message.total]),
                                    indicator: r.message.success > 0 ? 'green' : 'red'
                                });
                                listview.refresh();
                            }
                        }
                    });
                }
            );
        });
    }
};
