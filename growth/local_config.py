"""Read saved settings only when called by the loopback-only local launcher."""
from dotenv import dotenv_values


def read_local_settings(root):
    values=dotenv_values(root/'.env')
    return {'openai_key':values.get('OPENAI_API_KEY') or '',
            'tavily_key':values.get('TAVILY_API_KEY') or '',
            'model':values.get('OPENAI_MODEL') or values.get('MODEL_NAME') or 'gpt-6-luna'}
