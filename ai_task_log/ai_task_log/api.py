import frappe
import os
import json
from frappe.utils import now_datetime


@frappe.whitelist()
def process_prompt(prompt, model='gemini-3-flash-preview'):
    if not prompt or not prompt.strip():
        frappe.throw('Prompt is required', frappe.ValidationError)

    doc = frappe.get_doc({
        'doctype': 'AI Task Log',
        'prompt': prompt.strip(),
        'model': model,
        'status': 'Processing',
        'timestamp': now_datetime()
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    try:
        api_key = os.environ.get('GEMINI_API_KEY') or frappe.conf.get('gemini_api_key') or ''
        if not api_key:
            raise ValueError(
                'GEMINI_API_KEY not configured. '
                'Set GEMINI_API_KEY env var or add gemini_api_key to site_config.json'
            )

        import google.generativeai as genai
        genai.configure(api_key=api_key)

        gen_model = genai.GenerativeModel(model)
        response = gen_model.generate_content(prompt.strip())
        response_text = response.text

        doc.response = response_text
        doc.status = 'Completed'
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            'task_log': doc.name,
            'response': response_text,
            'status': 'Completed'
        }

    except Exception as e:
        doc.status = 'Failed'
        doc.error_message = str(e)
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            'task_log': doc.name,
            'response': None,
            'error': str(e),
            'status': 'Failed'
        }


@frappe.whitelist()
def retry_failed_tasks(task_names):
    if isinstance(task_names, str):
        task_names = json.loads(task_names)

    results = {'total': len(task_names), 'success': 0, 'failed': 0, 'details': []}

    for name in task_names:
        old_doc = frappe.get_doc('AI Task Log', name)
        if old_doc.status != 'Failed':
            results['details'].append({'name': name, 'status': 'skipped', 'reason': 'Not in Failed status'})
            continue

        old_doc.status = 'Processing'
        old_doc.error_message = ''
        old_doc.response = ''
        old_doc.save(ignore_permissions=True)
        frappe.db.commit()

        try:
            api_key = os.environ.get('GEMINI_API_KEY') or frappe.conf.get('gemini_api_key') or ''
            if not api_key:
                raise ValueError('GEMINI_API_KEY not configured')

            import google.generativeai as genai
            genai.configure(api_key=api_key)

            gen_model = genai.GenerativeModel(old_doc.model or 'gemini-3-flash-preview')
            response = gen_model.generate_content(old_doc.prompt)
            response_text = response.text

            old_doc.response = response_text
            old_doc.status = 'Completed'
            old_doc.save(ignore_permissions=True)
            frappe.db.commit()

            results['success'] += 1
            results['details'].append({'name': name, 'status': 'Completed'})

        except Exception as e:
            old_doc.status = 'Failed'
            old_doc.error_message = str(e)
            old_doc.save(ignore_permissions=True)
            frappe.db.commit()

            results['failed'] += 1
            results['details'].append({'name': name, 'status': 'Failed', 'error': str(e)})

    return results
