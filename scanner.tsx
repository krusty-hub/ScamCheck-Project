import { useState } from "react";
import {
  AlertTriangle,
  Check,
  ChevronRight,
  Link2,
  LoaderCircle,
  MessageSquareText,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type DemoState = "idle" | "analyzing" | "result";
type RiskLevel = "RED" | "YELLOW" | "GREEN";

type AnalysisResult = {
  score: number;
  level: RiskLevel;
  reasons: string[];
};

export function ScannerDemo({ compact = false }: { compact?: boolean }) {
  const [mode, setMode] = useState<"text" | "url">("text");
  const [value, setValue] = useState("");
  const [state, setState] = useState<DemoState>("idle");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function analyze() {
  const text = value.trim();

  if (!text) return;

  setState("analyzing");
  setError(null);
  setResult(null);

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/check_message?text=${encodeURIComponent(text)}`
    );

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data: AnalysisResult = await response.json();

    setResult(data);
    setState("result");
  } catch (err) {
  console.error("SCAN ERROR:", err);
  setError(err instanceof Error ? err.message : String(err));
  setState("idle");
}
}

  const levelStyles: Record<
    RiskLevel,
    {
      label: string;
      textClass: string;
      ringClass: string;
      borderClass: string;
      recommendation: string;
      title: string;
    }
  > = {
    RED: {
      label: "High risk",
      textClass: "text-high-risk",
      ringClass: "score-ring score-ring-red",
      borderClass: "border-high-risk",
      title: "Potential scam detected",
      recommendation:
        "Do not open the link or share personal information. Verify the request through an official channel.",
    },
    YELLOW: {
      label: "Medium risk",
      textClass: "text-yellow-600",
      ringClass: "score-ring score-ring-yellow",
      borderClass: "border-yellow-500",
      title: "Suspicious content detected",
      recommendation:
        "Proceed with caution. Do not share sensitive information until you verify the request through an official channel.",
    },
    GREEN: {
      label: "Low risk",
      textClass: "text-green-600",
      ringClass: "score-ring score-ring-green",
      borderClass: "border-green-500",
      title: "No significant threat detected",
      recommendation:
        "No significant suspicious indicators were detected. Continue to use normal caution when interacting with the message or link.",
    },
  };

  return (
    <div className={`scanner-shell ${compact ? "scanner-compact" : ""}`}>
      <div className="flex items-center justify-between border-b border-border px-4 py-3 sm:px-5">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase text-muted-foreground">
          <span className="status-dot" /> Detection console
        </div>
        <span className="font-mono text-[11px] text-muted-foreground">
          HEURISTIC v1.0
        </span>
      </div>

      <div className="p-4 sm:p-5">
        {!compact && (
          <div
            className="mb-4 inline-flex rounded-md bg-secondary p-1"
            aria-label="Scan type"
          >
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
                  setResult(null);
                  setError(null);
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

        <label
          className="mb-2 block text-xs font-semibold uppercase text-muted-foreground"
          htmlFor={compact ? "hero-sample" : "scanner-input"}
        >
          {mode === "text" ? "Content to inspect" : "Link to inspect"}
        </label>

        <Textarea
          id={compact ? "hero-sample" : "scanner-input"}
          value={value}
          onChange={(event) => {
            setValue(event.target.value);
            setState("idle");
            setResult(null);
            setError(null);
          }}
          placeholder={
            mode === "text"
              ? "Paste a suspicious message…"
              : "Paste a suspicious URL…"
          }
          className="min-h-28 resize-none bg-background p-4 leading-relaxed shadow-none sm:min-h-32"
        />

        {!compact && (
          <div className="mt-3 flex items-center justify-end gap-3">
            <Button
              type="button"
              onClick={analyze}
              disabled={!value.trim() || state === "analyzing"}
              className="h-10 shrink-0 px-5"
            >
              {state === "analyzing" ? (
                <LoaderCircle className="animate-spin" />
              ) : (
                <ChevronRight />
              )}
              {state === "analyzing" ? "Analyzing" : "Analyze"}
            </Button>
          </div>
        )}

        {error && (
          <div
            className="mt-5 rounded-md border border-destructive bg-secondary p-4 text-sm text-destructive"
            role="alert"
          >
            {error}
          </div>
        )}

        {state === "analyzing" && (
          <div
            className="mt-5 overflow-hidden rounded-md border border-border bg-secondary p-4"
            aria-live="polite"
          >
            <div className="mb-3 flex items-center justify-between text-xs font-medium">
              <span>Checking suspicious indicators</span>
              <span className="font-mono text-primary">PROCESSING</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-border">
              <div className="scan-progress h-full bg-primary" />
            </div>
          </div>
        )}

        {state === "result" && result && (
          <div
            className={`mt-5 rounded-md border bg-secondary p-4 sm:p-5 ${levelStyles[result.level].borderClass}`}
            aria-live="polite"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <div
                  className={`mb-1 flex items-center gap-2 text-xs font-bold uppercase ${levelStyles[result.level].textClass}`}
                >
                  <AlertTriangle className="size-4" />
                  {levelStyles[result.level].label}
                </div>

                <p className="font-display text-xl font-bold text-foreground">
                  {levelStyles[result.level].title}
                </p>
              </div>

              <div className={levelStyles[result.level].ringClass}>
                <strong>{result.score}</strong>
                <span>/100</span>
              </div>
            </div>

            <div className="mt-5 grid gap-2 sm:grid-cols-2">
              {result.reasons.map((reason, index) => (
                <div
                  key={`${reason}-${index}`}
                  className="flex items-center gap-2 rounded-sm bg-background px-3 py-2 text-xs text-foreground"
                >
                  <Check className="size-3.5 text-primary" />
                  {reason}
                </div>
              ))}
            </div>

            <div className="mt-4 border-l-2 border-primary pl-3 text-xs leading-relaxed text-muted-foreground">
              Recommended action: {levelStyles[result.level].recommendation}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
