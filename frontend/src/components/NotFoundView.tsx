import React from "react";
import { Link } from "react-router-dom";
import { Compass } from "lucide-react";
import { paths } from "@/routes";

export const NotFoundView: React.FC<{ message?: string }> = ({
  message = "O endereço que você abriu não existe.",
}) => (
  <main className="max-w-md mx-auto px-4 py-16 text-center">
    <Compass className="w-8 h-8 text-slate-300 mx-auto mb-3" />
    <h1 className="text-base font-bold text-slate-800">Página não encontrada</h1>
    <p className="text-xs text-slate-500 mt-1">{message}</p>
    <Link to={paths.home} className="btn-pink inline-block mt-4 px-4 py-1.5 text-xs font-bold rounded-sm">
      Voltar ao início
    </Link>
  </main>
);
