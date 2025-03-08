"use client";

import { Button } from "@/components/ui/button";

type InterestPromptModalProps = {
  onYes: () => void;
  onDontAsk: () => void;
};

export default function InterestPromptModal({
  onYes,
  onDontAsk,
}: InterestPromptModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-white/50">
      <div className="bg-white dark:bg-black rounded-lg p-6 w-96 shadow-lg">
        <h2 className="text-xl font-bold mb-2">Set Your Interests</h2>
        <p className="mb-4">
          It looks like you have not indicated any interests yet. Would you like
          to set them now?
        </p>
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={onDontAsk}>
            Do not Ask Again
          </Button>
          <Button onClick={onYes}>Yes</Button>
        </div>
      </div>
    </div>
  );
}
