import base64
import os
from openai import AsyncOpenAI


async def analyze_image(image_bytes: bytes, content_type: str) -> str:
    """Analisa imagem com GPT-4o Vision e retorna contexto de negócio."""
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{content_type};base64,{b64}"

    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Você é um analista de negócios especializado em branding e produtos. "
                        "Analise esta imagem (pode ser um produto, logo, protótipo, local físico ou material de marketing). "
                        "Responda em português com 3 parágrafos curtos:\n"
                        "1. O que você vê e identifica na imagem\n"
                        "2. Que tipo de negócio/produto isso representa e qual aparenta ser o posicionamento de mercado\n"
                        "3. Pontos fortes e oportunidades visuais percebidos (marca, design, apelo ao público)"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": data_url, "detail": "high"},
                },
            ],
        }],
        max_tokens=600,
    )
    return resp.choices[0].message.content.strip()
