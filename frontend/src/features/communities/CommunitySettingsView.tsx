import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { NotFoundView } from "@/components/NotFoundView";
import { ErrorState, LoadingState } from "@/components/StateViews";
import * as api from "@/services/communities";
import { errorMessage, fieldErrors, toApiError } from "@/services/errors";
import { paths } from "@/routes";
import type { Community, CommunityMemberItem } from "@/types";

const INPUT =
  "w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 focus:bg-white";

const Section: React.FC<{ title: string; danger?: boolean; children: React.ReactNode }> = ({ title, danger, children }) => (
  <section className={`panel-classic ${danger ? "border-red-300" : ""}`}>
    <div className="panel-classic-header">
      <h2 className={`text-sm font-bold ${danger ? "text-red-700" : "text-slate-800"}`}>{title}</h2>
    </div>
    <div className="p-4 space-y-3">{children}</div>
  </section>
);

function DetailsSection({ community, onSaved }: { community: Community; onSaved: (c: Community) => void }) {
  const [name, setName] = useState(community.name);
  const [description, setDescription] = useState(community.description ?? "");
  const [photo, setPhoto] = useState<File | null>(null);
  const [removePhoto, setRemovePhoto] = useState(false);
  const [banner, setBanner] = useState<File | null>(null);
  const [removeBanner, setRemoveBanner] = useState(false);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<{ ok: boolean; text: string } | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const preview = useMemo(() => (photo ? URL.createObjectURL(photo) : null), [photo]);
  useEffect(() => () => (preview ? URL.revokeObjectURL(preview) : undefined), [preview]);
  const bannerPreview = useMemo(() => (banner ? URL.createObjectURL(banner) : null), [banner]);
  useEffect(() => () => (bannerPreview ? URL.revokeObjectURL(bannerPreview) : undefined), [bannerPreview]);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setNotice(null);
    setErrors({});
    try {
      const updated = await api.updateCommunity(community.commname, { name, description, photo, removePhoto, banner, removeBanner });
      onSaved(updated);
      setPhoto(null);
      setRemovePhoto(false);
      setBanner(null);
      setRemoveBanner(false);
      setNotice({ ok: true, text: "Comunidade atualizada." });
    } catch (err) {
      setErrors(fieldErrors(err));
      setNotice({ ok: false, text: errorMessage(err) });
    } finally {
      setBusy(false);
    }
  };

  const current = removePhoto ? null : community.community_photo;
  const currentBanner = removeBanner ? null : community.banner_photo;
  return (
    <Section title="Dados da comunidade">
      <form onSubmit={save} className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="w-16 h-16 rounded-full overflow-hidden border border-slate-200 bg-purple-50 flex items-center justify-center text-purple-700 font-bold">
            {preview || current ? (
              <img src={preview ?? current ?? ""} alt="Foto da comunidade" className="w-full h-full object-cover" />
            ) : (
              community.name.charAt(0).toUpperCase()
            )}
          </div>
          <div className="space-y-1">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              aria-label="Nova foto da comunidade"
              onChange={(e) => {
                setPhoto(e.target.files?.[0] ?? null);
                setRemovePhoto(false);
              }}
              className="block text-[11px] text-slate-600"
            />
            {(community.community_photo || photo) && (
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
          </div>
        </div>
        <div>
          <span className="block mb-1 text-[11px] font-semibold text-slate-700">Banner do mural</span>
          <div className="w-full h-28 rounded-sm overflow-hidden border border-slate-200 bg-slate-50 flex items-center justify-center text-[11px] text-slate-400">
            {bannerPreview || currentBanner ? (
              <img src={bannerPreview ?? currentBanner ?? ""} alt="Banner da comunidade" className="w-full h-full object-cover" />
            ) : (
              "Sem banner"
            )}
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-3">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              aria-label="Novo banner da comunidade"
              onChange={(e) => {
                setBanner(e.target.files?.[0] ?? null);
                setRemoveBanner(false);
              }}
              className="block text-[11px] text-slate-600"
            />
            {(community.banner_photo || banner) && (
              <button
                type="button"
                onClick={() => {
                  setBanner(null);
                  setRemoveBanner(true);
                }}
                className="text-[11px] font-semibold text-red-700 hover:underline"
              >
                Remover banner
              </button>
            )}
          </div>
          <p className="text-[10px] text-slate-400 mt-0.5">Aparece no topo do mural da comunidade. Imagens largas funcionam melhor.</p>
          {errors.banner_photo && <p role="alert" className="text-[11px] text-red-700">{errors.banner_photo}</p>}
        </div>
        {errors.community_photo && <p role="alert" className="text-[11px] text-red-700">{errors.community_photo}</p>}
        <label className="block">
          <span className="block mb-1 text-[11px] font-semibold text-slate-700">Nome</span>
          <input value={name} onChange={(e) => setName(e.target.value)} maxLength={60} required className={INPUT} />
          {errors.name && <span role="alert" className="block mt-1 text-[11px] text-red-700">{errors.name}</span>}
        </label>
        <label className="block">
          <span className="block mb-1 text-[11px] font-semibold text-slate-700">Descrição ({description.length}/500)</span>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} maxLength={500} rows={4} className={INPUT} />
          {errors.description && <span role="alert" className="block mt-1 text-[11px] text-red-700">{errors.description}</span>}
        </label>
        {notice && (
          <p role={notice.ok ? "status" : "alert"} className={`text-[11px] font-semibold ${notice.ok ? "text-emerald-700" : "text-red-700"}`}>
            {notice.text}
          </p>
        )}
        <button disabled={busy} className="btn-pink px-4 py-1.5 text-xs font-bold rounded-sm disabled:opacity-60">
          {busy ? "Salvando..." : "Salvar"}
        </button>
      </form>
    </Section>
  );
}

function TransferSection({ community, onDone }: { community: Community; onDone: () => void }) {
  const [candidates, setCandidates] = useState<CommunityMemberItem[] | null>(null);
  const [target, setTarget] = useState("");
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const all: CommunityMemberItem[] = [];
      for (let page = 1; page <= 10; page++) {
        const data = await api.listMembers(community.commname, page);
        all.push(...data.results);
        if (!data.next) break;
      }
      if (!cancelled) setCandidates(all.filter((m) => m.role !== "LEADER" && m.current_state === "ACTIVE"));
    })().catch(() => !cancelled && setCandidates([]));
    return () => {
      cancelled = true;
    };
  }, [community.commname]);

  const confirm = async () => {
    setBusy(true);
    setError(null);
    try {
      await api.transferLeadership(community.commname, target);
      onDone();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Section title="Transferir liderança">
      <p className="text-[11px] text-slate-500">
        A pessoa escolhida passa a liderar a comunidade e você vira administrador. Só quem lidera pode excluir a comunidade.
      </p>
      {candidates === null ? (
        <LoadingState label="Carregando membros..." />
      ) : candidates.length === 0 ? (
        <p className="text-xs text-slate-500">Não há membros ativos para receber a liderança.</p>
      ) : (
        <>
          <select aria-label="Novo líder" value={target} onChange={(e) => setTarget(e.target.value)} className={INPUT}>
            <option value="">Escolha um membro...</option>
            {candidates.map((m) => (
              <option key={m.id} value={m.user.username}>
                {m.user.name} (@{m.user.username})
              </option>
            ))}
          </select>
          <button
            disabled={!target}
            onClick={() => setOpen(true)}
            className="px-4 py-1.5 text-xs font-bold rounded-sm border border-slate-300 text-slate-700 hover:bg-slate-100 disabled:opacity-50"
          >
            Transferir liderança
          </button>
        </>
      )}
      {open && (
        <ConfirmDialog
          title="Transferir liderança"
          confirmLabel="Transferir"
          busy={busy}
          error={error}
          onConfirm={() => void confirm()}
          onCancel={() => {
            setOpen(false);
            setError(null);
          }}
        >
          <p>
            Passar a liderança de <strong>{community.name}</strong> para <strong>@{target}</strong>? Você deixa de ser líder e não poderá desfazer
            sozinho.
          </p>
        </ConfirmDialog>
      )}
    </Section>
  );
}

function DeleteSection({ community }: { community: Community }) {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const confirm = async () => {
    setBusy(true);
    setError(null);
    try {
      // The dialog already checked the typed handle; the server checks it again.
      await api.deleteCommunity(community.commname, community.commname);
      navigate(paths.communities, { replace: true });
    } catch (err) {
      setError(errorMessage(err));
      setBusy(false);
    }
  };

  return (
    <Section title="Excluir comunidade" danger>
      <p className="text-xs text-slate-600">A comunidade some para todos. Esta ação não pode ser desfeita.</p>
      <button onClick={() => setOpen(true)} className="px-4 py-1.5 text-xs font-bold rounded-sm border border-red-300 text-red-700 hover:bg-red-50">
        Excluir comunidade
      </button>
      {open && (
        <ConfirmDialog
          title={`Excluir ${community.name}`}
          confirmLabel="Excluir definitivamente"
          requireText={community.commname}
          busy={busy}
          error={error}
          onConfirm={() => void confirm()}
          onCancel={() => {
            setOpen(false);
            setError(null);
          }}
        >
          <ul className="list-disc pl-4 space-y-1">
            <li>Publicações, membros e a página da comunidade deixam de existir para todos.</li>
            <li>O saldo de soap da comunidade e os itens de personalização comprados por ela serão perdidos.</li>
            <li>O identificador @{community.commname} volta a ficar disponível.</li>
          </ul>
        </ConfirmDialog>
      )}
    </Section>
  );
}

export const CommunitySettingsView: React.FC<{ commname: string }> = ({ commname }) => {
  const navigate = useNavigate();
  const [community, setCommunity] = useState<Community | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "notfound" | "forbidden" | "error">("loading");
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setStatus("loading");
    api
      .getCommunity(commname)
      .then((data) => {
        setCommunity(data);
        setStatus(data.permissions?.can_edit || data.permissions?.can_delete || data.permissions?.can_transfer_leadership ? "ready" : "forbidden");
      })
      .catch((err) => {
        if (toApiError(err).status === 404) setStatus("notfound");
        else {
          setError(errorMessage(err));
          setStatus("error");
        }
      });
  };
  useEffect(load, [commname]);

  if (status === "notfound") return <NotFoundView message="Esta comunidade não existe ou foi excluída." />;
  if (status === "loading") return <LoadingState />;
  if (status === "error" || !community) return <ErrorState message={error ?? "Não foi possível carregar."} onRetry={load} />;
  if (status === "forbidden") return <NotFoundView message="Você não pode configurar esta comunidade." />;

  const perms = community.permissions;
  return (
    <main className="max-w-2xl mx-auto px-3 sm:px-4 py-4 sm:py-6 space-y-4">
      <Link to={paths.community(commname)} className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-pink-700">
        <ArrowLeft className="w-3.5 h-3.5" />
        Voltar para {community.name}
      </Link>
      <h1 className="text-base font-bold text-slate-900">Configurações de @{community.commname}</h1>
      {perms?.can_edit && <DetailsSection community={community} onSaved={setCommunity} />}
      {perms?.can_transfer_leadership && (
        <TransferSection community={community} onDone={() => navigate(paths.community(commname), { replace: true })} />
      )}
      {perms?.can_delete && <DeleteSection community={community} />}
    </main>
  );
};
