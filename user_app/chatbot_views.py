import os
import json
import logging
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Configure logging
logger = logging.getLogger(__name__)

@csrf_exempt
def chatbot_api(request):
    """
    Independent API for the Agriculture Chatbot.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        # 1. Load API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return JsonResponse({'error': 'API key not configured in .env'}, status=500)

        # 2. Configure
        genai.configure(api_key=api_key)

        # 3. Parse request
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        language = data.get('language', 'en')

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # 4. Find an available model dynamically
        # This solves the 404 error by picking what the key actually supports
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority list of models to try
        target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro']
        selected_model = None
        
        for tm in target_models:
            if tm in available_models:
                selected_model = tm
                break
        
        if not selected_model:
            if available_models:
                selected_model = available_models[0] # Fallback to first available
            else:
                return JsonResponse({'error': 'No suitable AI models found for this key'}, status=500)

        logger.info(f"Chatbot using model: {selected_model}")
        model = genai.GenerativeModel(selected_model)

        # 5. Build prompt
        system_instruction = (
            "You are a helpful and simple Agriculture Assistant for Indian farmers. "
            "Provide short, practical advice on farming. Max 3 sentences."
        )
        lang_instruction = "Respond strictly in Marathi." if language == 'mr' else "Respond strictly in English."
        prompt = f"{system_instruction}\n\n{lang_instruction}\n\nUser: {user_message}"

        # 6. Generate content
        response = model.generate_content(prompt)
        
        if not response.text:
            return JsonResponse({'error': 'Empty response from AI'}, status=500)

        return JsonResponse({
            'response': response.text,
            'language': language
        })

    except Exception as e:
        logger.error(f"Chatbot Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
