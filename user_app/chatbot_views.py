import os
import json
import logging
import warnings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Suppress deprecation warnings from legacy SDK if installed
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

# Cached model instance to avoid per-request list_models() API calls
_CACHED_MODEL_NAME = None

AGRICULTURE_KNOWLEDGE = [
    {
        "keywords": ["jalgaon", "जळगाव", "जलगांव", "केळी", "केला"],
        "en": "Jalgaon district is renowned as the 'Banana City of India'. The best crops to produce in Jalgaon are Banana, Cotton, Sugarcane, Maize, Jowar (Sorghum), and Tur (Pigeon pea) due to its rich black fertile soil.",
        "mr": "जळगाव जिल्हा भारताची 'केळीची राजधानी' म्हणून प्रसिद्ध आहे. जळगावमधील काळ्या कसदार जमिनीत केळी, कापूस, ऊस, मका, ज्वारी आणि तूर ही पिके सर्वोत्तम येतात.",
        "hi": "जलगांव जिला भारत की 'केला राजधानी' के रूप में प्रसिद्ध है। जलगांव की काली उपजाऊ मिट्टी में केला, कपास, गन्ना, मक्का, ज्वार और अरहर की फसलें सबसे अच्छी होती हैं।"
    },
    {
        "keywords": ["nashik", "नाशिक", "नासिक", "द्राक्ष", "अंगूर", "कांदा", "प्याज"],
        "en": "Nashik is famous for Grapes, Onions, Tomatoes, Pomegranates, and Guava. The climate and soil in Nashik favor horticulture, vine crops, and vegetable production.",
        "mr": "नाशिक जिल्हा द्राक्षे, कांदा, टोमॅटो, डाळिंब आणि पेरूसाठी प्रसिद्ध आहे. नाशिकचे हवामान फळबाग आणि भाजीपाला पिकांसाठी अत्यंत अनुकूल आहे.",
        "hi": "नासिक जिला अंगूर, प्याज, टमाटर, अनार और अमरूद के लिए प्रसिद्ध है। नासिक की जलवायु और मिट्टी फलबागानों और सब्जियों के उत्पादन के लिए बेहद अनुकूल है।"
    },
    {
        "keywords": ["nagpur", "vidarbha", "नागपूर", "नागपुर", "विदर्भ", "संत्री", "संतरा"],
        "en": "Nagpur district is world-famous for Nagpur Oranges (Mandarin), Cotton, Soybean, Paddy (Rice), and Pigeon Pea (Tur).",
        "mr": "नागपूर जिल्हा नागपूरी संत्री, कापूस, सोयाबीन, धान (तांदूळ) आणि तुरीच्या उत्पादनासाठी जगप्रसिद्ध आहे.",
        "hi": "नागपुर जिला नागपुरी संतरे, कपास, सोयाबीन, धान (चावल) और अरहर के उत्पादन के लिए दुनिया भर में प्रसिद्ध है।"
    },
    {
        "keywords": ["pune", "satara", "पुणे", "सातारा", "सातारा"],
        "en": "Pune and Satara districts are ideal for Sugarcane, Wheat, Vegetables (Potato, Onion, Tomato), Flowers, and Fruits (Strawberry in Mahabaleshwar).",
        "mr": "पुणे आणि सातारा जिल्हे ऊस, गहू, बटाटा, कांदा, टोमॅटो, भाजीपाला आणि स्ट्रॉबेरी पिकांसाठी उत्तम आहेत.",
        "hi": "पुणे और सतारा जिले गन्ना, गेहूं, आलू, प्याज, टमाटर, सब्जियों, फूलों और महाबलेश्वर की स्ट्रॉबेरी फसलों के लिए सबसे उत्तम हैं।"
    },
    {
        "keywords": ["solapur", "ahmednagar", "सोलापूर", "सोलापुर", "अहमदनगर", "अहिल्यानगर"],
        "en": "Solapur and Ahmednagar excel in Pomegranate, Jowar (Sorghum), Sugarcane, Cotton, and Pulses due to favorable semi-arid soil conditions.",
        "mr": "सोलापूर आणि अहिल्यानगर (अहमदनगर) जिल्हे डाळिंब, ज्वारी, ऊस, कापूस आणि कडधान्य पिकांसाठी प्रसिद्ध आहेत.",
        "hi": "सोलापुर और अहमदनगर जिले अनार, ज्वार, गन्ना, कपास और दालों की फसलों के लिए अत्यधिक उपयुक्त हैं।"
    },
    {
        "keywords": ["konkan", "ratnagiri", "sindhudurg", "कोकण", "कोंकण", "रत्नागिरी", "सिंधुदुर्ग", "आंबा", "आम"],
        "en": "The Konkan coastal region (Ratnagiri, Sindhudurg, Raigad) is world-famous for Alphonso Mango (Hapus), Cashews, Coconuts, Arecanut, and Paddy (Rice).",
        "mr": "कोकण किनारपट्टी (रत्नागिरी, सिंधुदुर्ग, रायगड) हापूस आंबा, काजू, नारळ, सुपारी आणि भात शेतीसाठी प्रसिद्ध आहे.",
        "hi": "कोंकण तटीय क्षेत्र (रत्नागिरी, सिंधुदुर्ग, रायगढ़) हापुस आम, काजू, नारियल, सुपारी और धान की खेती के लिए प्रसिद्ध है।"
    },
    {
        "keywords": ["soil", "fertility", "organic", "manure", "fertil", "compost", "माती", "मातीची", "मिट्टी", "उर्वरता", "सुपीकता", "सुधारावी", "सेंद्रिय", "जैविक", "कंपोस्ट", "नत्र"],
        "en": "To improve soil fertility, apply well-rotted farmyard manure or organic compost to build soil organic carbon. Rotate cereal crops with nitrogen-fixing legumes (chickpeas, lentils) and balance pH (6.0–7.5).",
        "mr": "मातीची सुपीकता वाढवण्यासाठी सेंद्रिय खत किंवा कंपोस्ट खताचा वापर करा. कडधान्य पिकांची फेरपालट करून जमिनीतील नत्र वाढवा.",
        "hi": "मिट्टी की उर्वरता बढ़ाने के लिए अच्छी तरह सड़ी हुई गोबर की खाद या जैविक कंपोस्ट का उपयोग करें। दालों की फसलों का फेरबदल करके नाइट्रोजन बढ़ाएं।"
    },
    {
        "keywords": ["rain", "rainy", "monsoon", "season", "kharif", "पाऊस", "पावसाळा", "पावसाळ्यासाठी", "बारिश", "बरसात", "खरीफ", "हंगाम", "मौसम"],
        "en": "During the rainy (Kharif) season, Paddy (Rice), Soybean, Cotton, Maize, Jute, and Tur (Pigeon pea) perform best under high moisture conditions.",
        "mr": "पावसाळ्यात (खरीप हंगाम) भात (तांदूळ), सोयाबीन, कापूस, मका आणि तूर या पिकांची लागवड करणे सर्वात फायदेशीर ठरते.",
        "hi": "बारिश (खरीफ मौसम) के दौरान धान (चावल), सोयाबीन, कपास, मक्का और अरहर जैसी फसलों की बुवाई सबसे लाभदायक होती है।"
    },
    {
        "keywords": ["wheat", "rabi", "grain", "गहू", "गेहूं", "गव्हासाठी", "खत", "खाद", "डीएपी", "यूरिया"],
        "en": "For wheat crops, use balanced NPK application (120:60:40 kg/ha). Apply full Phosphorus (DAP) and Potassium (MOP) during sowing, and top-dress Urea during crown root initiation.",
        "mr": "गहू पिकासाठी एनपीके (120:60:40) चे संतुलित प्रमाण वापरा. पेरणीच्या वेळी डीएपी आणि एमओपी द्या आणि मुकुट मूळ फुटण्याच्या वेळी युरियाचा हप्ता द्या.",
        "hi": "गेहूं की फसल के लिए संतुलित एनपीके (120:60:40) का उपयोग करें। बुवाई के समय डीएपी और एमओपी दें और पहली सिंचाई पर यूरिया डालें।"
    },
    {
        "keywords": ["disease", "pest", "leaf", "spot", "yellow", "insect", "रोग", "कीट", "बीमारी", "डाग", "धब्बे", "पाने", "पत्तियां"],
        "en": "Inspect plant leaves early for spots or wilting. Remove infected leaves immediately, ensure proper row spacing for airflow, and use neem-based organic sprays or target fungicides.",
        "mr": "पिकांच्या पानांवर डाग किंवा पिवळेपणा दिसल्यास बाधित पाने काढून टाका. हवा खेळती राहण्यासाठी योग्य अंतर ठेवा आणि कडुनिंबाचे अर्काचे फवारणी करा.",
        "hi": "पत्तियों पर धब्बे या पीलापन दिखने पर प्रभावित पत्तियों को हटा दें। पौधों के बीच उचित दूरी रखें और नीम के तेल या जैविक स्प्रे का छिड़काव करें।"
    },
    {
        "keywords": ["water", "irrigation", "drip", "sprinkler", "पाणी", "पानी", "सिंचाई", "सिंचन", "ठिबक", "ड्रिप", "तुषार"],
        "en": "Adopt drip or sprinkler irrigation to conserve water and deliver nutrients directly to crop roots. Avoid waterlogging during flowering and seed development stages.",
        "mr": "पाणी बचतीसाठी ठिबक किंवा तुषार सिंचन पद्धतीचा वापर करा. फुले आणि फळे येण्याच्या काळात शेतात पाणी साचू देऊ नका.",
        "hi": "पानी की बचत के लिए ड्रिप या स्प्रिंकलर (फव्वारा) सिंचाई अपनाएं। फूल और फल आने के समय खेत में पानी जमा न होने दें।"
    }
]

def _get_knowledge_response(message, language):
    """Fallback Agriculture Knowledge Engine with score-based matching."""
    msg_lower = message.lower()
    best_match = None
    best_score = 0

    for entry in AGRICULTURE_KNOWLEDGE:
        score = sum(1 for kw in entry["keywords"] if kw in msg_lower)
        if score > best_score:
            best_score = score
            best_match = entry

    if best_match and best_score > 0:
        if language == 'hi':
            return best_match.get("hi", best_match["en"])
        elif language == 'mr':
            return best_match["mr"]
        else:
            return best_match["en"]

    # Dynamic fallback based on query context
    if any(word in msg_lower for word in ["पीक", "पिके", "फसल", "फसलों", "crop", "crops", "सर्वोत्तम", "सबसे"]):
        if language == 'hi':
            return "अपनी मिट्टी और मौसम के अनुसार खरीफ मौसम में धान, सोयाबीन, मक्का या कपास और रबी में गेहूं व चना फसलें सर्वोत्तम उपज देती हैं।"
        elif language == 'mr':
            return "तुमच्या भागातील माती आणि हवामानानुसार खरीप हंगामात भात, सोयाबीन, मका किंवा कापूस आणि रब्बी हंगामात गहू व हरभरा ही पिके सर्वोत्तम उत्पन्न देतात."
        return "Depending on your local soil and climate, crops like Rice, Soybean, Maize, or Cotton in Kharif and Wheat or Chickpea in Rabi yield best results."

    if any(word in msg_lower for word in ["खत", "खते", "खाद", "fertilizer", "fertility", "सुपीकता", "उर्वरता"]):
        if language == 'hi':
            return "मिट्टी की उर्वरता बढ़ाने के लिए सड़ी हुई गोबर की खाद या कंपोस्ट का उपयोग करें, फसलों का फेरबदल करें और एनपीके का संतुलित प्रयोग करें।"
        elif language == 'mr':
            return "मातीची सुपीकता वाढवण्यासाठी सेंद्रिय कंपोस्ट वापरा, पिकांची फेरपालट करा आणि माती परीक्षणानुसार NPK (नत्र, स्फुरद, पालाश) चे संतुलित प्रमाण द्या."
        return "To build soil fertility, apply organic compost, practice crop rotation with legumes, and maintain balanced NPK ratios based on soil testing."

    if language == 'hi':
        return "सर्वोत्तम फसल के लिए मिट्टी की जांच करवाएं और संतुलित उर्वरक का उपयोग करें। सही मौसम और फसल चक्र से उपज बढ़ती है।"
    elif language == 'mr':
        return "उत्कृष्ट पिकासाठी माती परीक्षण करून संतुलित खतांचा वापर करा. योग्य हवामान आणि पिकांच्या फेरपालटीमुळे उत्पादन वाढते."
    return "For optimal crop yields, perform periodic soil testing, use balanced NPK nutrients, and ensure crop rotation to preserve soil health."


def _get_model_name(api_key):
    """Retrieve and cache the best available Gemini model."""
    global _CACHED_MODEL_NAME
    if _CACHED_MODEL_NAME:
        return _CACHED_MODEL_NAME

    if not genai:
        return 'gemini-1.5-flash'

    genai.configure(api_key=api_key)
    try:
        available_models = [
            m.name for m in genai.list_models()
            if 'generateContent' in getattr(m, 'supported_generation_methods', [])
        ]
        target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro', 'gemini-1.5-flash']
        
        for tm in target_models:
            if tm in available_models:
                _CACHED_MODEL_NAME = tm
                return _CACHED_MODEL_NAME

        if available_models:
            _CACHED_MODEL_NAME = available_models[0]
            return _CACHED_MODEL_NAME
    except Exception as e:
        logger.warning(f"Model discovery fallback: {e}")

    _CACHED_MODEL_NAME = 'gemini-1.5-flash'
    return _CACHED_MODEL_NAME


@csrf_exempt
def chatbot_api(request):
    """
    Agriculture Chatbot API view with smart fallback.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = {}

    user_message = data.get('message', '').strip()
    language = data.get('language', 'en')

    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    api_key = os.environ.get("GEMINI_API_KEY")

    # Try Gemini API if package and valid key available
    if api_key and genai:
        try:
            genai.configure(api_key=api_key)
            model_name = _get_model_name(api_key)
            model = genai.GenerativeModel(model_name)

            system_instruction = (
                "You are a helpful and simple Agriculture Assistant for Indian farmers. "
                "Provide short, practical advice on farming. Max 3 sentences."
            )
            lang_map = {
                'hi': 'Respond strictly in Hindi.',
                'mr': 'Respond strictly in Marathi.',
                'en': 'Respond strictly in English.'
            }
            lang_instruction = lang_map.get(language, 'Respond strictly in English.')
            prompt = f"{system_instruction}\n\n{lang_instruction}\n\nUser: {user_message}"

            response = model.generate_content(prompt)

            if response and hasattr(response, 'text') and response.text:
                return JsonResponse({
                    'response': response.text,
                    'language': language
                })
        except Exception as e:
            logger.warning(f"Gemini API call failed, using Knowledge Engine fallback: {e}")

    # Seamless Fallback to Smart Agriculture Knowledge Engine
    answer = _get_knowledge_response(user_message, language)
    return JsonResponse({
        'response': answer,
        'language': language
    })
