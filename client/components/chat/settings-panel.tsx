/**
 * SettingsPanel Component
 *
 * Panel để config chat settings:
 * - Temperature slider
 * - Max tokens
 * - Enable thinking toggle
 * - System prompt
 */

"use client";

import { useState } from "react";
import {
  Settings,
  Brain,
  Thermometer,
  Hash,
  MessageSquare,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
} from "@/components/ui/sheet";
import { useChatStore } from "@/stores/chat-store";
import type { ChatSettings } from "@/lib/api/qwen";

export function SettingsPanel() {
  const { settings, updateSettings } = useChatStore();
  const [localSettings, setLocalSettings] = useState<ChatSettings>(settings);
  const [isOpen, setIsOpen] = useState(false);

  const handleSave = () => {
    updateSettings(localSettings);
    setIsOpen(false);
  };

  const handleReset = () => {
    const defaultSettings: ChatSettings = {
      temperature: 0.7,
      maxTokens: 32768,
      enableThinking: true,
      systemPrompt:
        "You are a helpful AI assistant with expertise in many topics. Show your reasoning process when enabled.",
    };
    setLocalSettings(defaultSettings);
    updateSettings(defaultSettings);
  };

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon" className="relative">
          <Settings className="w-5 h-5" />
          {settings.enableThinking && (
            <Badge
              variant="secondary"
              className="absolute -top-1 -right-1 h-4 w-4 p-0 flex items-center justify-center text-[10px]"
            >
              <Brain className="w-2.5 h-2.5" />
            </Badge>
          )}
        </Button>
      </SheetTrigger>

      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Chat Settings
          </SheetTitle>
          <SheetDescription>
            Configure how Qwen3 generates responses
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-4 p-4">
          {/* Temperature */}
          <Card>
            <CardHeader className="pb-4 space-y-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Thermometer className="w-4 h-4" />
                  Temperature
                </CardTitle>
                <Badge variant="secondary" className="font-mono text-xs">
                  {localSettings.temperature}
                </Badge>
              </div>
              <CardDescription className="text-xs leading-relaxed">
                Controls randomness. Lower = more focused, Higher = more
                creative
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Slider
                value={[localSettings.temperature]}
                onValueChange={([value]) =>
                  setLocalSettings({ ...localSettings, temperature: value })
                }
                min={0}
                max={2}
                step={0.1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground px-1">
                <span>Focused</span>
                <span>Balanced</span>
                <span>Creative</span>
              </div>
            </CardContent>
          </Card>

          {/* Max Tokens */}
          <Card>
            <CardHeader className="pb-4 space-y-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Hash className="w-4 h-4" />
                  Max Tokens
                </CardTitle>
                <Badge variant="secondary" className="font-mono text-xs">
                  {localSettings.maxTokens}
                </Badge>
              </div>
              <CardDescription className="text-xs leading-relaxed">
                Maximum length of response (1 token ≈ 0.75 words)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Slider
                value={[localSettings.maxTokens]}
                onValueChange={([value]) =>
                  setLocalSettings({ ...localSettings, maxTokens: value })
                }
                min={512}
                max={32768}
                step={512}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground px-1">
                <span>512</span>
                <span>16K</span>
                <span>32K</span>
              </div>
            </CardContent>
          </Card>

          {/* Thinking Mode */}
          <Card className="border-2">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 flex-1">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Brain className="w-4 h-4 text-primary" />
                  </div>
                  <div className="space-y-1">
                    <CardTitle className="text-sm font-medium">
                      Thinking Mode
                    </CardTitle>
                    <CardDescription className="text-xs leading-relaxed">
                      Show AI reasoning process before answer
                    </CardDescription>
                  </div>
                </div>
                <Switch
                  checked={localSettings.enableThinking}
                  onCheckedChange={(checked) =>
                    setLocalSettings({
                      ...localSettings,
                      enableThinking: checked,
                    })
                  }
                />
              </div>
            </CardHeader>
          </Card>

          <Separator className="my-4" />

          {/* System Prompt */}
          <div className="space-y-3">
            <Label
              htmlFor="system-prompt"
              className="flex items-center gap-2 text-sm font-medium"
            >
              <MessageSquare className="w-4 h-4" />
              System Prompt
            </Label>
            <Textarea
              id="system-prompt"
              value={localSettings.systemPrompt}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  systemPrompt: e.target.value,
                })
              }
              placeholder="Customize AI personality and behavior..."
              className="min-h-[100px] resize-none text-sm"
            />
            <p className="text-xs text-muted-foreground leading-relaxed">
              Defines AI&apos;s role and behavior. Be specific for best results.
            </p>
          </div>
        </div>

        <SheetFooter className="gap-2 pt-4 border-t">
          <Button variant="outline" onClick={handleReset} className="flex-1">
            Reset to Defaults
          </Button>
          <Button onClick={handleSave} className="flex-1">
            Save Changes
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
