import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class AITaskLog(Document):
    def before_insert(self):
        if not self.timestamp:
            self.timestamp = now_datetime()
        if not self.status:
            self.status = 'Pending'

    def before_save(self):
        if self.status == 'Completed' and not self.response:
            frappe.throw('Response is required when status is Completed')
