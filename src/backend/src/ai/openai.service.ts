import { Injectable } from '@nestjs/common';
import OpenAI from 'openai';

@Injectable()
export class OpenAIService {
  private openai: OpenAI;

  constructor() {
    this.openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  }

  async generateSceneText(sceneId: string, profile: any): Promise<string> {
    const prompt = this.buildScenePrompt(sceneId, profile);
    
    const response = await this.openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: `Ты — сценарист интерактивной эротической истории «Живая Книга». 
Пиши от первого лица героини. Стиль: чувственный, женский взгляд, 5 чувств, медленное нарастание.
Адаптируй текст под профиль читателя.`,
        },
        { role: 'user', content: prompt },
      ],
      max_tokens: 800,
      temperature: 0.85,
    });

    return response.choices[0]?.message?.content || '';
  }

  async generateImage(prompt: string, profile: any): Promise<string | null> {
    const enhancedPrompt = this.enhanceImagePrompt(prompt, profile);
    
    try {
      const response = await this.openai.images.generate({
        model: 'dall-e-3',
        prompt: enhancedPrompt,
        size: '1024x1024',
        quality: 'standard',
        n: 1,
      });

      return response.data[0]?.url || null;
    } catch (error) {
      console.error('Image generation failed:', error);
      return null;
    }
  }

  private buildScenePrompt(sceneId: string, profile: any): string {
    return `Сцена: ${sceneId}
Профиль читателя:
- romanticism: ${profile?.romanticism || 5}
- sensuality: ${profile?.sensuality || 5}
- dominance: ${profile?.dominance || 5}
- boldness: ${profile?.boldness || 5}

Напиши текст сцены (300-500 слов) от первого лица.
Если sensuality > 6 — больше физических ощущений.
Если romanticism > 6 — больше эмоций и предвкушения.
Если dominance > 6 — героиня контролирует ситуацию.`;
  }

  private enhanceImagePrompt(prompt: string, profile: any): string {
    const baseStyle = 'Cinematic photography, soft lighting, shallow depth of field, moody color grading, film grain, 35mm lens, warm palette';
    const safetyFilter = 'Sensual but tasteful, no explicit nudity, female gaze perspective';
    
    return `${prompt}. ${baseStyle}. ${safetyFilter}.`;
  }
}