import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { OpenAIService } from '../ai/openai.service';
import { RedisService } from '../redis/redis.service';

@Injectable()
export class StoryService {
  constructor(
    private prisma: PrismaService,
    private openai: OpenAIService,
    private redis: RedisService,
  ) {}

  async getCurrentScene(userId: string) {
    const progress = await this.prisma.storyProgress.findUnique({
      where: { userId },
    });

    if (!progress) {
      // Initialize new user at scene 0
      await this.prisma.storyProgress.create({
        data: { userId, currentSceneId: 'scene_00', flags: [] },
      });
      return this.getSceneById('scene_00');
    }

    return this.getSceneById(progress.currentSceneId);
  }

  async processChoice(userId: string, choiceId: string) {
    const choice = await this.prisma.choice.findUnique({
      where: { choiceId },
      include: { scene: true },
    });

    if (!choice) throw new Error('Choice not found');

    // Apply effects to profile
    const effects = choice.effects as Record<string, number>;
    await this.updateProfile(userId, effects);

    // Update progress
    await this.prisma.storyProgress.update({
      where: { userId },
      data: {
        currentSceneId: choice.nextSceneId,
      },
    });

    // Record choice
    await this.prisma.userChoice.create({
      data: { userId, choiceId: choice.id },
    }).catch(() => {}); // Ignore duplicates

    // Invalidate cache
    await this.redis.del(`scene:${userId}:${choice.nextSceneId}`);

    return this.getSceneWithAdaptation(userId, choice.nextSceneId);
  }

  async getSceneWithAdaptation(userId: string, sceneId: string) {
    const cacheKey = `scene:${userId}:${sceneId}`;
    const cached = await this.redis.get(cacheKey);
    if (cached) return JSON.parse(cached);

    const profile = await this.prisma.profile.findUnique({
      where: { userId },
    });

    const scene = await this.getSceneById(sceneId);

    // Determine which text variant to use
    let text = scene.textDefault;
    if (profile) {
      if (profile.romanticism > 7 && scene.textRomantic) {
        text = scene.textRomantic;
      } else if (profile.dominance > 7 && scene.textDominant) {
        text = scene.textDominant;
      }
    }

    // Generate AI-adapted illustration prompt
    let illustrationUrl = null;
    if (scene.illustrationPrompt) {
      illustrationUrl = await this.openai.generateImage(
        scene.illustrationPrompt,
        profile,
      );
    }

    const result = {
      ...scene,
      text,
      illustrationUrl,
    };

    await this.redis.set(cacheKey, JSON.stringify(result), 3600);
    return result;
  }

  private async getSceneById(sceneId: string) {
    return this.prisma.scene.findUnique({
      where: { sceneId },
      include: { choices: true },
    });
  }

  private async updateProfile(userId: string, effects: Record<string, number>) {
    const updateData: Record<string, { increment: number }> = {};
    for (const [key, value] of Object.entries(effects)) {
      updateData[key] = { increment: value };
    }

    await this.prisma.profile.update({
      where: { userId },
      data: updateData,
    });
  }
}