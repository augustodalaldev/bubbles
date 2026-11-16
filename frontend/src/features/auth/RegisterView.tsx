import React, { useState } from "react";
import { BrandLogo } from "@/components/BrandLogo";
import { SoapIcon } from "@/components/SoapIcon";
import { api } from "@/services/api";
import { useAuthStore } from "./authStore";
import { ArrowRight, AlertCircle } from "lucide-react";

interface RegisterViewProps {
  onNavigateToLogin: () => void;
  onRegisterSuccess: () => void;
}

export const RegisterView: React.FC<RegisterViewProps> = ({
  onNavigateToLogin,
  onRegisterSuccess,
}) => {
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [password, setPassword] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setUser = useAuthStore((s) => s.setUser);

  // Validate 14 years minimum age (Backend requirement RF001)
  const isAtLeast14YearsOld = (dateStr: string): boolean => {
    if (!dateStr) return false;
    const birth = new Date(dateStr);
    const today = new Date();
    const minAgeDate = new Date(today.getFullYear() - 14, today.getMonth(), today.getDate());
    return birth <= minAgeDate;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim() || !username.trim() || !email.trim() || !birthDate || !password) {
      setError("Preencha todos os campos obrigatórios.");
      return;
    }

    if (!isAtLeast14YearsOld(birthDate)) {
      setError("É necessário ter pelo menos 14 anos para participar da rede.");
      return;
    }

    setLoading(true);

    try {
      const res = await api.post("/auth/register/", {
        name: name.trim(),
        username: username.trim().toLowerCase(),
        email: email.trim(),
        birth_date: birthDate,
        password,
        description: description.trim(),
      });

      if (res.data?.tokens?.access) {
        localStorage.setItem("bubbles_access_token", res.data.tokens.access);
        if (res.data.tokens.refresh) {
          localStorage.setItem("bubbles_refresh_token", res.data.tokens.refresh);
        }
      }

      setUser(res.data.user);
      onRegisterSuccess();
    } catch (err: any) {
      const data = err.response?.data;
      const msg = 
        data?.message || 
        data?.username?.[0] || 
        data?.email?.[0] || 
        data?.birth_date?.[0] || 
        data?.detail || 
        "Erro ao criar conta. Verifique os dados.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md panel-classic shadow-md overflow-hidden bg-white">
        
        {/* Header Bar */}
        <div className="panel-classic-header justify-center py-3 bg-slate-50 border-b border-slate-200">
          <BrandLogo height={30} />
        </div>

        {/* Content Box */}
        <div className="p-6">
          <div className="mb-4 text-center">
            <h2 className="text-base font-bold text-slate-800">
              Criar nova conta
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Junte-se à rede social de bolhas e conexões
            </p>
          </div>

          {/* Signup Bonus Notice */}
          <div className="mb-4 p-2.5 bg-pink-50 border border-pink-200 rounded-sm text-xs text-pink-900 flex items-center gap-2">
            <SoapIcon size={20} />
            <div>
              <span className="font-bold">Bônus de Boas-Vindas:</span> Ganhe{" "}
              <strong>20 soap</strong> ao criar sua conta para apoiar posts e customizar seu perfil.
            </div>
          </div>

          {error && (
            <div className="mb-4 p-2.5 bg-red-50 border border-red-200 rounded-sm text-xs text-red-800 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="grid grid-cols-2 gap-2.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Nome completo *
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Seu nome"
                  className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 focus:bg-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Nome de usuário *
                </label>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value.replace(/[^a-zA-Z0-9_]/g, ""))}
                  placeholder="ex: lucas_aero"
                  className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 focus:bg-white"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  E-mail *
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com"
                  className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 focus:bg-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Nascimento (mín 14 anos) *
                </label>
                <input
                  type="date"
                  required
                  value={birthDate}
                  onChange={(e) => setBirthDate(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 focus:bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Senha *
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mínimo 6 caracteres"
                className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 focus:bg-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Descrição do perfil (opcional)
              </label>
              <textarea
                rows={2}
                maxLength={250}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Conte brevemente sobre seus interesses..."
                className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 focus:bg-white resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-pink py-2 text-xs font-bold rounded-sm mt-3 flex items-center justify-center gap-1.5"
            >
              <span>{loading ? "Cadastrando..." : "Criar conta e receber 20 soap"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>

        {/* Footer / Switch to Login */}
        <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 text-center text-xs text-slate-600">
          Já possui conta?{" "}
          <button
            onClick={onNavigateToLogin}
            className="font-bold text-pink-600 hover:underline"
          >
            Entrar
          </button>
        </div>

      </div>
    </div>
  );
};
