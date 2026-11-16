import React, { useState } from "react";
import { BrandLogo } from "@/components/BrandLogo";
import { api } from "@/services/api";
import { useAuthStore } from "./authStore";
import { MOCK_USER } from "@/features/profile/mockData";
import { ArrowRight, AlertCircle, Lock, User as UserIcon } from "lucide-react";

interface LoginViewProps {
  onNavigateToRegister: () => void;
  onLoginSuccess: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({
  onNavigateToRegister,
  onLoginSuccess,
}) => {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setUser = useAuthStore((s) => s.setUser);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim() || !password) {
      setError("Informe seu usuário/e-mail e sua senha.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await api.post("/auth/login/", {
        identifier: identifier.trim(),
        password,
      });

      if (res.data?.tokens?.access) {
        localStorage.setItem("bubbles_access_token", res.data.tokens.access);
        if (res.data.tokens.refresh) {
          localStorage.setItem("bubbles_refresh_token", res.data.tokens.refresh);
        }
      }

      setUser(res.data.user || MOCK_USER);
      onLoginSuccess();
    } catch (err: any) {
      const msg = err.response?.data?.message || err.response?.data?.detail || "Usuário ou senha incorretos.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // Quick shortcut for demo review
  const handleQuickDemoLogin = () => {
    setUser(MOCK_USER);
    onLoginSuccess();
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-sm panel-classic shadow-md overflow-hidden bg-white">
        
        {/* Header Bar */}
        <div className="panel-classic-header justify-center py-3 bg-slate-50 border-b border-slate-200">
          <BrandLogo height={30} />
        </div>

        {/* Content Box */}
        <div className="p-6">
          <div className="mb-5 text-center">
            <h2 className="text-base font-bold text-slate-800">
              Acessar sua conta
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Entre para ver suas bolhas, amigos e cartas
            </p>
          </div>

          {error && (
            <div className="mb-4 p-2.5 bg-pink-50 border border-pink-200 rounded-sm text-xs text-pink-900 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-pink-600 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Usuário ou e-mail
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="ex: marina_aqua ou marina@bubbles.social"
                  className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-pink-500 focus:bg-white"
                />
                <UserIcon className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-semibold text-slate-700">
                  Senha
                </label>
                <a href="#recuperar" className="text-[11px] text-pink-600 hover:underline">
                  Esqueceu a senha?
                </a>
              </div>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-pink-500 focus:bg-white"
                />
                <Lock className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-pink py-2 text-xs font-bold rounded-sm mt-4 flex items-center justify-center gap-1.5"
            >
              <span>{loading ? "Entrando..." : "Entrar"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          {/* Quick Demo Shortcut */}
          <div className="mt-4 pt-3 border-t border-slate-200 text-center">
            <button
              onClick={handleQuickDemoLogin}
              type="button"
              className="text-xs font-semibold text-purple-600 hover:text-purple-800 hover:underline"
            >
              Entrar direto como Marina Santos (@marina_aqua)
            </button>
          </div>
        </div>

        {/* Footer / Switch to Register */}
        <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 text-center text-xs text-slate-600">
          Ainda não tem conta?{" "}
          <button
            onClick={onNavigateToRegister}
            className="font-bold text-pink-600 hover:underline"
          >
            Cadastre-se e ganhe 20 soap
          </button>
        </div>

      </div>
    </div>
  );
};
