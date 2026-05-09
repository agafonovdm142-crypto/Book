import { Controller, Get, Post, Body, UseGuards, Req } from '@nestjs/common';
import { StoryService } from './story.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@Controller('api/v1/story')
export class StoryController {
  constructor(private readonly storyService: StoryService) {}

  @Get('current')
  @UseGuards(JwtAuthGuard)
  async getCurrentScene(@Req() req) {
    return this.storyService.getCurrentScene(req.user.userId);
  }

  @Post('choice')
  @UseGuards(JwtAuthGuard)
  async makeChoice(
    @Req() req,
    @Body('choiceId') choiceId: string,
  ) {
    return this.storyService.processChoice(req.user.userId, choiceId);
  }

  @Get('scene/:sceneId')
  @UseGuards(JwtAuthGuard)
  async getScene(@Req() req, @Body('sceneId') sceneId: string) {
    return this.storyService.getSceneWithAdaptation(req.user.userId, sceneId);
  }
}