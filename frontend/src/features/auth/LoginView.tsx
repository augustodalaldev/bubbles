import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { paths } from "@/routes";
import { BrandLogo } from "@/components/BrandLogo";
import { errorMessage } from "@/services/errors";
import { useAuthStore } from "./authStore";
import { PasswordInput } from "@/components/PasswordInput";
import { ArrowRight, AlertCircle, User as UserIcon } from "lucide-react";

export const LoginView: React.FC = () => {
  const { search } = useLocation();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useAuthStore((s) => s.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim() || !password) {
      setError("Informe seu usuário ou e-mail e a sua senha.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await login(identifier.trim(), password);
    } catch (err) {
      setError(errorMessage(err));
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-sm panel-classic shadow-md overflow-hidden bg-white">
        <div className="panel-classic-header justify-center py-3 bg-slate-50 border-b border-slate-200">
          <BrandLogo height={30} />
        </div>

        <div className="p-6">
          <div className="mb-5 text-center">
            <h2 className="text-base font-bold text-slate-800">Acessar sua conta</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Entre para ver suas bolhas, amigos e cartas
            </p>
          </div>

          {error && (
            <div
              role="alert"
              className="mb-4 p-2.5 bg-pink-50 border border-pink-200 rounded-sm text-xs text-pink-900 flex items-start gap-2"
            >
              <AlertCircle className="w-4 h-4 text-pink-600 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label htmlFor="login-identifier" className="block text-xs font-semibold text-slate-700 mb-1">
                Usuário ou e-mail
              </label>
              <div className="relative">
                <input
                  id="login-identifier"
                  type="text"
                  autoComplete="username"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="ex: marina_aqua ou marina@email.com"
                  className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-pink-500 focus:bg-white"
                />
                <UserIcon className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <div>
              <label htmlFor="login-password" className="block text-xs font-semibold text-slate-700 mb-1">
                Senha
              </label>
              <PasswordInput
                id="login-password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-pink-500 focus:bg-white"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-pink py-2 text-xs font-bold rounded-sm mt-4 flex items-center justify-center gap-1.5 disabled:opacity-60"
            >
              <span>{loading ? "Entrando..." : "Entrar"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>

        <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 text-center text-xs text-slate-600">
          Ainda não tem conta?{" "}
          <Link to={paths.register + search} className="font-bold text-pink-600 hover:underline">
            Cadastre-se e ganhe soap de boas-vindas
          </Link>
        </div>
      </div>
    </div>
  );
};
