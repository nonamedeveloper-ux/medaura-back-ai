import ssl
import httpx
from typing import Any, Dict, List
from google import genai
from app.config import settings

# Corporate proxy SSL fix
ssl._create_default_https_context = ssl._create_unverified_context

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL = "gemini-3-flash-preview"

RISK_KEYWORDS = ["yaxshi bo'ldim", "to'xtataman", "samarasiz", "to'xtatmoqchiman"]
NEGATIVE_WORDS = ["og'riq", "yomon", "bezovta", "qo'rqaman", "dahshatli", "azob"]
POSITIVE_WORDS = ["yaxshi", "zoʻr", "rahmat", "yordam", "ajoyib", "baxtli"]

PHASE_TECHNIQUES = {
    "initial": "habit_formation",
    "improvement": "loss_aversion",
    "consolidation": "progress_visualization",
    "completion": "achievement_focus",
}


def _generate(prompt: str) -> str:
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


class GeminiService:
    def chat(self, patient_context: Dict[str, Any], message: str) -> Dict[str, Any]:
        prompt = f"""Siz tibbiy AI yordamchisisiz. Professional va samimiy bo'ling.

BEMOR:
- Ismi: {patient_context.get('name', 'Bemor')}
- Yoshi: {patient_context.get('age', "noma'lum")}
- Tashxis: {patient_context.get('diagnosis', "noma'lum")}
- Kun: {patient_context.get('current_day', 0)}/{patient_context.get('total_days', 0)}
- Adherence: {patient_context.get('adherence_rate', 0)}%

XAVFLI HOLATLAR:
- "Yaxshi bo'ldim" → OGOHLANTIR (kasallik qaytishi xavfi)
- "Samarasiz" → SABR tavsiya qil
- "Yon ta'sir" → SHIFOKORGA yo'naltir

Javobingiz: qisqa (2-3 jumla), tushunarli, emoji bilan.

Bemor: {message}

Javob:"""

        try:
            text = _generate(prompt)
            requires_attention = any(kw in message.lower() for kw in RISK_KEYWORDS)
            return {
                "response": text.strip(),
                "requires_doctor_attention": requires_attention,
                "sentiment": self._analyze_sentiment(message),
                "model": MODEL,
            }
        except Exception as e:
            print(f"Gemini chat error: {e}")
            return {
                "response": "Kechirasiz, xatolik yuz berdi. Shifokoringizga murojaat qiling.",
                "requires_doctor_attention": True,
                "sentiment": "error",
                "model": MODEL,
            }

    def generate_reminder(self, patient_context: Dict[str, Any], phase: str) -> Dict[str, Any]:
        technique = PHASE_TECHNIQUES.get(phase, "positive_reinforcement")
        prompt = f"""Bemor uchun motivatsion eslatma yarat.

BEMOR: {patient_context.get('name')}
FASE: {phase}
KUN: {patient_context.get('current_day')}
TEXNIKA: {technique}

QOIDALAR:
- 2 jumla, qisqa
- Psixologik texnika: {technique}
- Emoji qo'shish
- Motivatsion ton

ESLATMA:"""

        try:
            text = _generate(prompt)
            return {
                "message": text.strip(),
                "phase": phase,
                "psychological_technique": technique,
                "tone": "motivational",
            }
        except Exception as e:
            print(f"Gemini reminder error: {e}")
            return {
                "message": "Dori ichishni unutmang! Sog'lig'ingiz muhim. 💊",
                "phase": phase,
                "psychological_technique": technique,
                "tone": "motivational",
            }

    def assess_risk(
        self,
        patient_id: str,
        adherence_data: Dict[str, Any],
        chat_history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        adherence_rate = adherence_data.get("adherence_rate", 0)
        streak = adherence_data.get("streak", 0)

        score = 0.0
        if adherence_rate < 50:
            score += 40
        elif adherence_rate < 70:
            score += 20
        if streak == 0:
            score += 20
        elif streak < 3:
            score += 10

        negative_messages = sum(
            1 for m in chat_history[-10:]
            if m.get("role") == "user"
            and any(kw in m.get("content", "").lower() for kw in RISK_KEYWORDS)
        )
        score = min(score + negative_messages * 10, 100)

        if score >= 70:
            level = "critical"
        elif score >= 50:
            level = "high"
        elif score >= 30:
            level = "medium"
        else:
            level = "low"

        return {
            "risk_score": round(score, 1),
            "risk_level": level,
            "recommendations": self._build_recommendations(level, adherence_data),
        }

    def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        sentiment = self._analyze_sentiment(message)
        urgency = "high" if any(kw in message.lower() for kw in RISK_KEYWORDS) else "low"
        keywords = [w for w in NEGATIVE_WORDS + RISK_KEYWORDS if w in message.lower()]
        return {"sentiment": sentiment, "urgency": urgency, "keywords": keywords}

    def _analyze_sentiment(self, message: str) -> str:
        msg = message.lower()
        if any(w in msg for w in NEGATIVE_WORDS):
            return "negative"
        if any(w in msg for w in POSITIVE_WORDS):
            return "positive"
        return "neutral"

    def _build_recommendations(self, level: str, data: Dict) -> List[str]:
        recs = []
        if level in ("critical", "high"):
            recs.append("Darhol shifokor bilan bog'laning")
            recs.append("Bemorga shaxsiy qo'ng'iroq qiling")
        if data.get("adherence_rate", 100) < 70:
            recs.append("Dori qabul jadvalini ko'rib chiqing")
        if data.get("streak", 1) == 0:
            recs.append("Motivatsion eslatmalar yuborishni kuchaytiring")
        if not recs:
            recs.append("Hozirgi davolanish jarayonini davom ettiring")
        return recs


gemini_service = GeminiService()
