import React from 'react';
import { AlertTriangle } from 'lucide-react';
import type { PendingAction } from '../hooks/useChat';

interface ChatPendingActionsProps {
  actions: PendingAction[];
  disabled: boolean;
  onAnswer: (actionId: number, approve: boolean) => void;
}

// Deletes the assistant asked for. Nothing is deleted until the user clicks Confirm.
export const ChatPendingActions: React.FC<ChatPendingActionsProps> = ({ actions, disabled, onAnswer }) => {
  if (actions.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      {actions.map((action) => (
        <div key={action.id} className="border border-red-200 bg-red-50 rounded-xl p-3 text-sm">
          <div className="flex items-start gap-2 text-red-800">
            <AlertTriangle size={18} className="shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Please confirm</p>
              <p>{action.description}?</p>
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-3">
            <button
              type="button"
              onClick={() => onAnswer(action.id, false)}
              disabled={disabled}
              className="btn btn-secondary text-sm px-3 py-1.5"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => onAnswer(action.id, true)}
              disabled={disabled}
              className="px-3 py-1.5 rounded-lg bg-red-600 text-white font-semibold hover:bg-red-700 disabled:opacity-50"
            >
              Confirm
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
