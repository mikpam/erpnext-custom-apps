import frappe
from frappe.tests.utils import FrappeTestCase
from ai_task_log.ai_task_log.api import process_prompt


class TestAITaskLog(FrappeTestCase):
    def test_create_task_log(self):
        doc = frappe.get_doc({
            'doctype': 'AI Task Log',
            'prompt': 'What is 2+2?',
            'status': 'Pending'
        })
        doc.insert()
        self.assertEqual(doc.status, 'Pending')
        self.assertIsNotNone(doc.timestamp)
        self.assertTrue(doc.name.startswith('AITL-'))

    def test_completed_requires_response(self):
        doc = frappe.get_doc({
            'doctype': 'AI Task Log',
            'prompt': 'Test prompt',
            'status': 'Completed'
        })
        self.assertRaises(frappe.ValidationError, doc.insert)

    def test_completed_with_response(self):
        doc = frappe.get_doc({
            'doctype': 'AI Task Log',
            'prompt': 'Hello',
            'response': 'Hi there!',
            'status': 'Completed'
        })
        doc.insert()
        self.assertEqual(doc.status, 'Completed')
        self.assertEqual(doc.response, 'Hi there!')

    def test_process_prompt_without_api_key(self):
        import os
        old_key = os.environ.pop('GEMINI_API_KEY', None)
        try:
            result = process_prompt(prompt='Test')
            doc = frappe.get_doc('AI Task Log', result['task_log'])
            self.assertEqual(doc.status, 'Failed')
            self.assertIn('GEMINI_API_KEY', doc.error_message)
        finally:
            if old_key:
                os.environ['GEMINI_API_KEY'] = old_key

    def test_process_prompt_missing_prompt(self):
        self.assertRaises(frappe.ValidationError, process_prompt, prompt='')

    def tearDown(self):
        frappe.db.rollback()
