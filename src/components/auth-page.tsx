import { useState } from "react";
import { ArrowRight, Loader2, Lock, Mail, ShieldCheck, AlertCircle } from "lucide-react";
// Adjust these imports based on your routing (e.g., Next.js uses next/navigation)
import { useNavigate } from '@tanstack/react-router';

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScamlexBrand } from "@/components/scamlex-brand";
import { supabase } from "@/lib/supabase"; // Your Supabase client instance

export function ScamlexAuth() {
  const navigate = useNavigate();
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        // Supabase might require email confirmation depending on your settings
        setError("Check your email for the confirmation link!"); 
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        // Successful login, redirect to dashboard
        navigate({ to: "/dashboard" }); // Fixed here
      }
    } catch (err: any) {
      setError(err.message || "An error occurred during authentication.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-background text-foreground">
      {/* Left Panel - Branding & Info */}
      <div className="hidden lg:flex flex-col justify-between bg-secondary p-12 border-r border-border">
        <div>
          <ScamlexBrand />
          <h1 className="mt-12 font-display text-4xl font-bold leading-tight">
            Protect your digital perimeter.
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-md">
            Sign in to access your cached query history, API keys, and explainable risk scoring dashboard.
          </p>
        </div>
        
        <div className="space-y-6">
          <div className="flex items-center gap-3 text-sm font-medium">
            <ShieldCheck className="size-5 text-primary" />
            <span>End-to-end encrypted sessions</span>
          </div>
          <div className="rounded-md border border-border bg-background p-6">
            <blockquote className="space-y-4">
              <p className="text-sm leading-6 text-muted-foreground">
                "Scamlex turns vague warnings into deterministic, explainable verdicts. The dashboard is essential for my daily analysis."
              </p>
              <footer className="text-sm font-semibold">Security Analyst</footer>
            </blockquote>
          </div>
        </div>
      </div>

      {/* Right Panel - Auth Form */}
      <div className="flex items-center justify-center p-8 sm:p-12">
        <div className="w-full max-w-md space-y-8">
          <div className="lg:hidden mb-10">
            <ScamlexBrand />
          </div>
          
          <div className="space-y-2">
            <h2 className="text-3xl font-display font-bold tracking-tight">
              {isSignUp ? "Create an account" : "Welcome back"}
            </h2>
            <p className="text-sm text-muted-foreground">
              {isSignUp 
                ? "Enter your details to start analyzing web threats." 
                : "Enter your credentials to access your dashboard."}
            </p>
          </div>

          <form onSubmit={handleAuth} className="space-y-6">
            {error && (
              <div className="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive border border-destructive/20">
                <AlertCircle className="size-4 shrink-0" />
                <p>{error}</p>
              </div>
            )}

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
                  <Input 
                    id="email"
                    type="email" 
                    placeholder="name@example.com" 
                    className="pl-10"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                  {!isSignUp && (
                    <a href="#forgot" className="text-xs font-medium text-primary hover:underline">
                      Forgot password?
                    </a>
                  )}
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
                  <Input 
                    id="password"
                    type="password" 
                    placeholder="••••••••" 
                    className="pl-10"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>
            </div>

            <Button type="submit" className="w-full h-11" disabled={loading}>
              {loading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <>
                  {isSignUp ? "Sign up" : "Sign in"} 
                  <ArrowRight className="ml-2 size-4" />
                </>
              )}
            </Button>
          </form>

          <div className="text-center text-sm text-muted-foreground">
            {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
            <button 
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError(null);
              }}
              className="font-semibold text-foreground hover:text-primary hover:underline transition-colors"
            >
              {isSignUp ? "Sign in" : "Sign up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}