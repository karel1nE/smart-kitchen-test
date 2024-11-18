from fastapi import FastAPI, HTTPException
import uvicorn
from g4f.client import Client
from pydantic import BaseModel
from typing import List

prompt = """
Напиши рецепт из данных ингридиентов: {}.
Тебе надо написать ответ в таком формате без какого либо дополнительного текста:
### Название рецепта
### Ингридиенты
### Процесс приготовления

Если ничего приготовить из этого нельзя напиши только одно слово NO
"""

app = FastAPI()

class IngredientsList(BaseModel):
    ingredients: list[str]

@app.post("/request")
async def generate_recipe(ingredients_list: IngredientsList) -> str:
    client = Client()
    response = None

    for _ in range(3):  
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt.format(ingredients_list.ingredients)}],
            )
            answer = response.choices[0].message.content.strip()
            if "404" not in answer:
                if answer == "NO":
                    raise HTTPException(status_code=400, detail="Unable to generate a recipe with the provided ingredients.")
                return answer
        except Exception as _:
            continue

    raise HTTPException(status_code=500, detail="Failed to connect GPT")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1488)