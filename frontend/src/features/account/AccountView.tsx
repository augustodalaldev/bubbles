import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Avatar } from "@/components/Avatar";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { PasswordInput } from "@/components/PasswordInput";
import { useAuthStore } from "@/features/auth/authStore";
import * as accountApi from "@/services/account";
import { errorMessage, fieldErrors, toApiError } from "@/services/errors";
import { paths } from "@/routes";

const INPUT =
  "w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 focus:bg-white";

type Notice = { kind: "ok" | "error"; text: string } | null;

const Section: React.FC<{ title: string; hint?: string; danger?: boolean; children: React.ReactNode }> = ({
  title,
  hint,
  danger,
  children,
}) => (
  <section className={`panel-classic ${danger ? "border-red-300" : ""}`}>
    <div className="panel-classic-header">
      <h2 className={`text-sm font-bold ${danger ? "text-red-700" : "text-slate-800"}`}>{title}</h2>
    </div>
    <div className="p-4 space-y-3">
      {hint && <p className="text-[11px] text-slate-500">{hint}</p>}
      {children}
    </div>
  </section>
);

const Field: React.FC<{ label: string; error?: string; children: React.ReactNode }> = ({ label, error, children }) => (
  <label className="block">
    <span className="block mb-1 text-[11px] font-semibold text-slate-700">{label}</span>
    {children}
    {error && (
      <span role="alert" className="block mt-1 text-[11px] text-red-700">
        {error}
      </span>
    )}
  </label>
);

const NoticeLine: React.FC<{ notice: Notice }> = ({ notice }) =>
  notice ? (
    <p role={notice.kind === "error" ? "alert" : "status"} className={`text-[11px] font-semibold ${notice.kind === "ok" ? "text-emerald-700" : "text-red-700"}`}>
      {notice.text}
    </p>
  ) : null;

function ProfileSection() {
  const user = useAuthStore((s) => s.user)!;
  const setUser = useAuthStore((s) => s.setUser);
  const [name, setName] = useState(user.name);
  const [description, setDescription] = useState(user.description ?? "");
  const [birthDate, setBirthDate] = useState(user.birth_date ?? "");
  const [photo, setPhoto] = useState<File | null>(null);
  const [removePhoto, setRemovePhoto] = useState(false);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<Notice>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const preview = useMemo(() => (photo ? URL.createObjectURL(photo) : null), [photo]);
  useEffect(() => () => (preview ? URL.revokeObjectURL(preview) : undefined), [preview]);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setNotice(null);
    setErrors({});
    try {
      const updated = await accountApi.updateProfile({ name, description, birthDate, photo, removePhoto });
      setUser({ ...user, ...updated });
      setPhoto(null);
      setRemovePhoto(false);
      setNotice({ kind: "ok", text: "Perfil atualizado." });
    } catch (err) {
      setErrors(fieldErrors(err));
      setNotice({ kind: "error", text: errorMessage(err) });
    } finally {
      setBusy(false);
    }
  };

  const shownUser = removePhoto ? { ...user, profile_photo: null } : user;
  return (
    <Section title="Perfil" hint={`Seu @ (${user.username}) não pode ser alterado.`}>
      <form onSubmit={save} className="space-y-3">
        <div className="flex items-center gap-3">
          {preview ? (
            <img src={preview} alt="Nova foto" className="w-16 h-16 rounded-full object-cover border border-slate-200" />
          ) : (
            <Avatar user={shownUser} className="w-16 h-16" />
          )}
          <div className="space-y-1">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              aria-label="Nova foto de perfil"
              onChange={(e) => {
                setPhoto(e.target.files?.[0] ?? null);
                setRemovePhoto(false);
              }}
              className="block text-[11px] text-slate-600"
            />
            {(user.profile_photo || photo) && (
              <button
                type="button"
                onClick={() => {
                  setPhoto(null);
                  setRemovePhoto(true);
                }}
                className="text-[11px] font-semibold text-red-700 hover:underline"
              >
                Remover foto
              </button>
            )}
            {removePhoto && <span className="block text-[10px] text-slate-500">A foto será removida ao salvar.</span>}
          </div>
        </div>
        {errors.profile_photo && <p role="alert" className="text-[11px] text-red-700">{errors.profile_photo}</p>}
        <Field label="Nome" error={errors.name}>
          <input value={name} onChange={(e) => setName(e.target.value)} maxLength={50} required className={INPUT} />
        </Field>
        <Field label={`Descrição (${description.length}/250)`} error={errors.description}>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} maxLength={250} rows={3} className={INPUT} />
        </Field>
        <Field label="Data de nascimento" error={errors.birth_date}>
          <input type="date" value={birthDate} onChange={(e) => setBirthDate(e.target.value)} required className={INPUT} />
        </Field>
        <NoticeLine notice={notice} />
        <button disabled={busy} className="btn-pink px-4 py-1.5 text-xs font-bold rounded-sm disabled:opacity-60">
          {busy ? "Salvando..." : "Salvar perfil"}
        </button>
      </form>
    </Section>
  );
}

function PasswordSection() {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<Notice>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setNotice(null);
    setErrors({});
    if (next !== confirm) {
      setErrors({ confirm: "As senhas não são iguais." });
      return;
    }
    setBusy(true);
    try {
      await accountApi.changePassword(current, next);
      setCurrent("");
      setNext("");
      setConfirm("");
      setNotice({ kind: "ok", text: "Senha alterada. Os outros aparelhos foram desconectados." });
    } catch (err) {
      const fields = fieldErrors(err);
      const code = toApiError(err).code;
      setErrors(code === "invalid_password" ? { current: errorMessage(err) } : { next: fields.new_password ?? "" });
      setNotice({ kind: "error", text: errorMessage(err) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Section title="Senha">
      <form onSubmit={save} className="space-y-3">
        <Field label="Senha atual" error={errors.current}>
          <PasswordInput value={current} onChange={(e) => setCurrent(e.target.value)} autoComplete="current-password" required className={INPUT} />
        </Field>
        <Field label="Nova senha" error={errors.next}>
          <PasswordInput value={next} onChange={(e) => setNext(e.target.value)} autoComplete="new-password" required className={INPUT} />
        </Field>
        <Field label="Repita a nova senha" error={errors.confirm}>
          <PasswordInput value={confirm} onChange={(e) => setConfirm(e.target.value)} autoComplete="new-password" required className={INPUT} />
        </Field>
        <NoticeLine notice={notice} />
        <button disabled={busy} className="btn-pink px-4 py-1.5 text-xs font-bold rounded-sm disabled:opacity-60">
          {busy ? "Salvando..." : "Alterar senha"}
        </button>
      </form>
    </Section>
  );
}

function EmailSection() {
  const user = useAuthStore((s) => s.user)!;
  const setUser = useAuthStore((s) => s.setUser);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<Notice>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setNotice(null);
    setErrors({});
    try {
      const updated = await accountApi.changeEmail(password, email);
      setUser({ ...user, ...updated });
      setEmail("");
      setPassword("");
      setNotice({ kind: "ok", text: "E-mail atualizado." });
    } catch (err) {
      const fields = fieldErrors(err);
      setErrors({ email: fields.new_email ?? "", password: fields.password ?? "" });
      setNotice({ kind: "error", text: errorMessage(err) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Section title="E-mail" hint={`E-mail atual: ${user.email ?? ""}`}>
      <form onSubmit={save} className="space-y-3">
        <Field label="Novo e-mail" error={errors.email}>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" className={INPUT} />
        </Field>
        <Field label="Senha atual" error={errors.password}>
          <PasswordInput value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required className={INPUT} />
        </Field>
        <NoticeLine notice={notice} />
        <button disabled={busy} className="btn-pink px-4 py-1.5 text-xs font-bold rounded-sm disabled:opacity-60">
          {busy ? "Salvando..." : "Alterar e-mail"}
        </button>
      </form>
    </Section>
  );
}

function DeleteSection() {
  const user = useAuthStore((s) => s.user)!;
  const endSession = useAuthStore((s) => s.endSession);
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [leaderOf, setLeaderOf] = useState<string[]>([]);
  const balance = user.soap_balance ?? user.wallet?.soap_balance ?? 0;

  const close = () => {
    setOpen(false);
    setPassword("");
    setError(null);
    setLeaderOf([]);
  };

  const confirm = async () => {
    setBusy(true);
    setError(null);
    setLeaderOf([]);
    try {
      await accountApi.deleteAccount(password);
      endSession();
      navigate(paths.login, { replace: true });
    } catch (err) {
      const apiError = toApiError(err);
      if (apiError.code === "must_transfer_leadership") {
        setLeaderOf((apiError.extra.communities as string[]) ?? []);
      }
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Section title="Excluir conta" danger>
      <p className="text-xs text-slate-600">
        Sua conta será anonimizada e você não poderá mais entrar. Esta ação não pode ser desfeita.
      </p>
      <button onClick={() => setOpen(true)} className="px-4 py-1.5 text-xs font-bold rounded-sm border border-red-300 text-red-700 hover:bg-red-50">
        Excluir minha conta
      </button>
      {open && (
        <ConfirmDialog
          title="Excluir conta"
          confirmLabel="Excluir definitivamente"
          requireText="EXCLUIR"
          busy={busy}
          error={error}
          onConfirm={() => void confirm()}
          onCancel={close}
        >
          <ul className="list-disc pl-4 space-y-1">
            <li>Suas publicações e comentários continuam, mas aparecem como “Conta excluída”.</li>
            <li>Foto, descrição, seguidores, quem você segue, participações em comunidades e bubblepops são removidos.</li>
            <li>
              Seu saldo de <strong>{balance} soap</strong> e seus itens de personalização serão perdidos.
            </li>
            <li>Se você lidera uma comunidade, transfira a liderança ou exclua a comunidade antes.</li>
          </ul>
          {leaderOf.length > 0 && (
            <p className="font-semibold">
              Você lidera:{" "}
              {leaderOf.map((c, i) => (
                <React.Fragment key={c}>
                  {i > 0 && ", "}
                  <Link to={paths.communitySettings(c)} className="underline text-pink-700" onClick={close}>
                    @{c}
                  </Link>
                </React.Fragment>
              ))}
            </p>
          )}
          <Field label="Sua senha">
            <PasswordInput value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" className={INPUT} />
          </Field>
        </ConfirmDialog>
      )}
    </Section>
  );
}

export const AccountView: React.FC = () => {
  const user = useAuthStore((s) => s.user)!;
  return (
    <main className="max-w-2xl mx-auto px-3 sm:px-4 py-4 sm:py-6 space-y-4">
      <Link to={paths.profile(user.username)} className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-pink-700">
        <ArrowLeft className="w-3.5 h-3.5" />
        Voltar ao perfil
      </Link>
      <h1 className="text-base font-bold text-slate-900">Minha conta</h1>
      <ProfileSection />
      <PasswordSection />
      <EmailSection />
      <DeleteSection />
    </main>
  );
};
