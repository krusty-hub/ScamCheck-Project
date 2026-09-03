import { useState } from "react";
import { AlertTriangle, Check, ChevronRight, Link2, LoaderCircle, MessageSquareText } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type DemoState = "idle" | "analyzing" | "result";

const demoText = "URGENT: Your account has been locked. Verify immediately at secure-pay0ut-login.co to prevent suspension.";

export function ScannerDemo({ compact = false }: { compact?: boolean }) {
  const [mode, setMode] = useState<"text" | "url">("text");
  const [value, setValue] = useState(compact ? demoText : "");
  const [state, setState] = useState<DemoState>(compact ? "result" : "idle");

  function analyze() {
    if (!value.trim()) return;
    setState("analyzing");
    window.setTimeout(() => setState("result"), 1100);
  }

  return (
    <div className={`scanner-shell ${compact ? "scanner-compact" : ""}`}>
      <div className="flex items-center justify-between border-b border-border px-4 py-3 sm:px-5">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase text-muted-foreground">
          <span className="status-dot" /> Detection console
        </div>
        <span className="font-mono text-[11px] text-muted-foreground">HEURISTIC v1.0</span>
      </div>

      <div className="p-4 sm:p-5">
        {!compact && (
          <div className="mb-4 inline-flex rounded-md bg-secondary p-1" aria-label="Scan type">
            {(["text", "url"] as const).map((item) => (
              <Button
                key={item}
                type="button"
                size="sm"
                variant={mode === item ? "default" : "ghost"}
                onClick={() => {
                  setMode(item);
                  setState("idle");
                  setValue("");
                }}
                aria-pressed={mode === item}
                className="h-8 shadow-none"
              >
                {item === "text" ? <MessageSquareText /> : <Link2 />}
                {item === "text" ? "Message" : "URL"}
              </Button>
            ))}
          </div>
        )}

        <label className="mb-2 block text-xs font-semibold uppercase text-muted-foreground" htmlFor={compact ? "hero-sample" : "scanner-input"}>
          {mode === "text" ? "Content to inspect" : "Link to inspect"}
        </label>
        <Textarea
          id={compact ? "hero-sample" : "scanner-input"}
          value={value}
          onChange={(event) => {
            setValue(event.target.value);
            setState("idle");
          }}
          placeholder={mode === "text" ? "Paste a suspicious message…" : "Paste a suspicious URL…"}
          className="min-h-28 resize-none bg-background p-4 leading-relaxed shadow-none sm:min-h-32"
        />

        {!compact && (
          <div className="mt-3 flex items-center justify-between gap-3">
            <p className="text-xs text-muted-foreground">Demonstration only — connect the REST API for live analysis.</p>
            <Button type="button" onClick={analyze} disabled={!value.trim() || state === "analyzing"} className="h-10 shrink-0 px-5">
              {state === "analyzing" ? <LoaderCircle className="animate-spin" /> : <ChevronRight />}
              {state === "analyzing" ? "Analyzing" : "Analyze"}
            </Button>
          </div>
        )}

        {state === "analyzing" && (
          <div className="mt-5 overflow-hidden rounded-md border border-border bg-secondary p-4" aria-live="polite">
            <div className="mb-3 flex items-center justify-between text-xs font-medium">
              <span>Checking suspicious indicators</span><span className="font-mono text-primary">PROCESSING</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-border"><div className="scan-progress h-full bg-primary" /></div>
          </div>
        )}

        {state === "result" && (
          <div className="mt-5 rounded-md border border-border bg-secondary p-4 sm:p-5" aria-live="polite">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="mb-1 flex items-center gap-2 text-xs font-bold uppercase text-high-risk"><AlertTriangle className="size-4" /> High risk</div>
                <p className="font-display text-xl font-bold text-foreground">Potential scam detected</p>
              </div>
              <div className="score-ring"><strong>84</strong><span>/100</span></div>
            </div>
            <div className="mt-5 grid gap-2 sm:grid-cols-2">
              {["Urgent call to action", "Account threat language", "Character substitution", "Unfamiliar domain pattern"].map((reason) => (
                <div key={reason} className="flex items-center gap-2 rounded-sm bg-background px-3 py-2 text-xs text-foreground">
                  <Check className="size-3.5 text-primary" /> {reason}
                </div>
              ))}
            </div>
            <div className="mt-4 border-l-2 border-primary pl-3 text-xs leading-relaxed text-muted-foreground">
              Recommended action: do not open the link or share personal information. Verify the request through an official channel.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}