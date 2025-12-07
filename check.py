import google.generativeai as genai
import os

# Pega a chave dos Segredos
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("ERRO: Chave não encontrada nos Secrets!")
else:
    genai.configure(api_key=api_key)
    print("--- MODELOS DISPONÍVEIS PARA VOCÊ ---")
    try:
        for m in genai.list_models():
            # Filtra apenas modelos que geram conteúdo (chat)
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Erro ao listar: {e}")
