frappe.ui.form.on('AI Task Log', {
    refresh: function(frm) {
        if (frm.doc.status === 'Failed') {
            frm.add_custom_button(__('Retry'), function() {
                frappe.call({
                    method: 'ai_task_log.ai_task_log.api.retry_failed_tasks',
                    args: { task_names: [frm.doc.name] },
                    freeze: true,
                    freeze_message: __('Retrying...'),
                    callback: function(r) {
                        if (r.message && r.message.success > 0) {
                            frappe.show_alert({
                                message: __('Task retried successfully'),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        } else {
                            frappe.show_alert({
                                message: __('Retry failed'),
                                indicator: 'red'
                            });
                            frm.reload_doc();
                        }
                    }
                });
            }, __('Actions'));
        }
    }
});
