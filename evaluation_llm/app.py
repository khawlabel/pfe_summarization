import google.generativeai as genai
import os
from prompt import *
from prompt import evaluate_summary_template, rules, guidelines
from langchain_groq import ChatGroq

GROQ_API_KEY_2="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"
GEMINI_API_KEY="AIzaSyCTjsJSsPV689EO0j-NtcD8AOGNq68BpSU"
# Configure the generative AI model
genai.configure(api_key=GEMINI_API_KEY )

# Instantiate the generative AI regular model
model = genai.GenerativeModel('gemini-1.5-flash')
    
# Instantiate the generative AI QA model with the response mime type set to JSON a
QA_model = genai.GenerativeModel('gemini-1.5-flash',
                                 generation_config = {"response_mime_type":"application/json"})
LLM_NAME_4="llama3-8b-8192"

llm=ChatGroq(groq_api_key=GROQ_API_KEY_2, model_name=LLM_NAME_4)


def call_model(model: genai, prompt:str):
    response = model.generate_content(prompt)
    return response.text
def call_model_groq(model, prompt: str):
    return model.invoke(prompt)


def evaluate_summary(query, context, summary):
    full_prompt = evaluate_summary_template.format(
        rules=rules,
        guidelines=guidelines,
        query=query,
        context=context,
        summary=summary
    )
    result = call_model_groq(llm, full_prompt)
    return result

query ="Fais un résumé clair et structuré des informations disponibles."

context = """
\n\n\nAKHBAR EL 01١1\n\nÀ | A\nAKHBARELYOUM ٠\nMEDIAMARKETING Page : 16 Pdl \u200fأخبار\u200e\n\u200eLe : mercredi 09 oct. 2024 @ * ê __\n\nHydrocarbures\n\nwWww.akhbarelyoum-dz\n\n:HI O*“llng\n\n\u200e2E —\u200f + ليا لجا 6 \u200epA\u200f كه نبا نيا\nتوقيع مذكرهة تماهم مع شركة قطريهة\nوقعت الوكاكة الوطنية لتثمين موارد المحروقات (التغط). أمس الثلاثاء\nبالجزائر العاصمة. مذكرة تشاهم مع شركة "غلف بتروليوم ليميتد"\nالقطرية. تهدف إلى تعزيز روابط التعاون بين الطرفين في مجال المحروفقات\nبالجزائر. حسب ما أكدته الوكالة في بيان لها.\nوجرث مراسم توقيع مذكرةٌ الثقاهم يمقر "النفط". تحت إشراف رئيسها . مراد\nيلجهم. بحضور وقد فقطري رفيع المستوى. إضافة إلى أعضاء اللجنة المديرة\n
للوكالة. يضيف ذات المصدر. وتهدف الوثيقة. وفقا للبيان. إلى "تسهيل\nوتعزيز روابط التعاون بين الطرفين في مجال المحروقات. لا 
سيما من خلال\nالعرض الذي خدمنك وكالة النفغط لشركة الخحليج للبرول حول فرص\nالاستتمارفي قطاع استكشاف وإتتاجالمحروقات بالجزائر .
"""

summary = """
Le ministère des Hydrocarbures a annoncé la signature d'une mémorandum d'entente avec la société qatarie Gulf Petroleum Limited, à Alger, le 09 octobre 2024. Cette entente vise à renforcer les liens de coopération entre les deux parties dans le domaine des hydrocarbures en Algérie, notamment en ce qui concerne les opportunités d'investissement dans l'exploration et la production des hydrocarbures dans le pays.
"""

result = evaluate_summary(query, context, summary)
print(result)

