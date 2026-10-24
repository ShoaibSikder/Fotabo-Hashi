import { useCallback, useEffect, useState } from 'react';
import { FileText, Megaphone, Plus, Save, Trash2, UsersRound, X } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Input from '../../../components/ui/Input.jsx';
import Textarea from '../../../components/ui/Textarea.jsx';
import Button from '../../../components/ui/Button.jsx';
import Pagination from '../../../components/ui/Pagination.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import Avatar from '../../../components/ui/Avatar.jsx';
import ResponsiveDetailPanel from '../../../components/ui/ResponsiveDetailPanel.jsx';
import { apiDelete, apiGet, apiPatch, apiPost } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

const emptyNotice = { title: '', content: '', is_published: false };
const emptyMember = { name: '', designation: '', social_url: '', image: null, display_order: 0, is_published: true };

export default function AdminPublicContentPage() {
  const { t } = useLang();
  const [tab, setTab] = useState('members');

  return (
    <div className="space-y-6">
      <h1 className="font-heading text-2xl font-extrabold tracking-tight text-slate-950 sm:text-3xl">{t('adminPublicContent')}</h1>
      <div className="flex gap-2 border-b border-slate-200" role="tablist" aria-label={t('adminPublicContent')}>
        <button type="button" role="tab" aria-selected={tab === 'members'} onClick={() => setTab('members')} className={`inline-flex min-h-11 cursor-pointer items-center gap-2 border-b-2 px-3 text-sm font-bold transition-colors ${tab === 'members' ? 'border-brand text-brand' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>
          <UsersRound size={16} /> {t('activeMembersAdmin')}
        </button>
        <button type="button" role="tab" aria-selected={tab === 'notices'} onClick={() => setTab('notices')} className={`inline-flex min-h-11 cursor-pointer items-center gap-2 border-b-2 px-3 text-sm font-bold transition-colors ${tab === 'notices' ? 'border-brand text-brand' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>
          <Megaphone size={16} /> {t('managePublicNotices')}
        </button>
      </div>
      {tab === 'members' ? <MemberManager /> : <NoticeManager />}
    </div>
  );
}

function MemberAvatar({ member, size = 'sm' }) {
  const [failed, setFailed] = useState(false);
  if (member.image && !failed) {
    return <img src={member.image} alt="" onError={() => setFailed(true)} className={`${size === 'lg' ? 'h-20 w-20' : 'h-10 w-10'} shrink-0 rounded-full object-cover`} />;
  }
  return <Avatar name={member.name} size={size} />;
}

function MemberManager() {
  const { t } = useLang();
  const [members, setMembers] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [form, setForm] = useState(emptyMember);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');
  const [feedback, setFeedback] = useState('');

  const loadMembers = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiGet(`${API_ENDPOINTS.adminMembers}?page=${page}`);
      const results = Array.isArray(data) ? data : data?.results || [];
      setMembers(results);
      setCount(Array.isArray(data) ? results.length : data?.count || 0);
      setSelected((current) => current ? results.find((member) => member.id === current.id) || null : null);
    } catch (err) {
      setError(err.message);
      setMembers([]);
      setCount(0);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => { loadMembers(); }, [loadMembers]);

  useEffect(() => {
    setForm(selected ? {
      name: selected.name || '',
      designation: selected.designation || '',
      social_url: selected.social_url || '',
      image: null,
      display_order: selected.display_order ?? 0,
      is_published: Boolean(selected.is_published),
    } : emptyMember);
  }, [selected]);

  function updateField(event) {
    const { name, value, checked, type, files } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : type === 'file' ? files?.[0] || null : value,
    }));
  }

  async function saveMember(event) {
    event.preventDefault();
    setSaving(true);
    setError('');
    setFeedback('');
    const body = new FormData();
    body.append('name', form.name.trim());
    body.append('designation', form.designation.trim());
    body.append('social_url', form.social_url.trim());
    body.append('display_order', String(form.display_order));
    body.append('is_published', String(form.is_published));
    if (form.image) body.append('image', form.image);

    try {
      const saved = selected
        ? await apiPatch(API_ENDPOINTS.adminMemberDetail(selected.id), body)
        : await apiPost(API_ENDPOINTS.adminMembers, body);
      setMembers((current) => selected
        ? current.map((member) => member.id === saved.id ? saved : member).sort((a, b) => a.display_order - b.display_order || a.id - b.id)
        : [...current, saved].sort((a, b) => a.display_order - b.display_order || a.id - b.id).slice(0, 20));
      setCount((current) => selected ? current : current + 1);
      setSelected(saved);
      setFeedback(t('memberSaved'));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function deleteMember() {
    if (!selected || !window.confirm(t('confirmDeleteMember'))) return;
    setDeleting(true);
    setError('');
    setFeedback('');
    try {
      await apiDelete(API_ENDPOINTS.adminMemberDetail(selected.id));
      setMembers((current) => current.filter((member) => member.id !== selected.id));
      setCount((current) => Math.max(0, current - 1));
      setSelected(null);
      setEditorOpen(false);
      setFeedback(t('memberDeleted'));
    } catch (err) {
      setError(err.message);
    } finally {
      setDeleting(false);
    }
  }

  return <ContentManagerFrame error={error} feedback={feedback}>
    <div className="grid items-start gap-5 2xl:grid-cols-[1.1fr_.9fr]">
      <Card className="!border-slate-200 !bg-white !p-4 !shadow-sm sm:!p-5">
        <div className="mb-4 flex items-center justify-between gap-3"><h2 className="font-heading text-lg font-extrabold text-slate-900">{t('activeMembersAdmin')}</h2><Button type="button" variant="primary" onClick={() => { setSelected(null); setEditorOpen(true); setError(''); setFeedback(''); }}><Plus size={16} /> {t('newMember')}</Button></div>
        {loading ? <div className="py-12"><Spinner label={t('loading')} /></div> : members.length ? <>
          <div className="space-y-2">{members.map((member) => <button key={member.id} type="button" onClick={() => { setSelected(member); setEditorOpen(true); setFeedback(''); setError(''); }} className={`flex w-full cursor-pointer items-center gap-3 rounded-xl border p-3 text-left transition-colors hover:border-rose-200 hover:bg-rose-50/40 ${selected?.id === member.id ? 'border-rose-200 bg-rose-50/50' : 'border-slate-100 bg-white'}`}>
            <MemberAvatar member={member} />
            <span className="min-w-0 flex-1"><span className="block truncate text-sm font-extrabold text-slate-800">{member.name}</span><span className="mt-0.5 block truncate text-xs text-slate-500">{member.designation || member.social_url}</span></span>
            <span className="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold text-slate-600">#{member.display_order}</span>
            <span className={`rounded-full px-2 py-1 text-[10px] font-extrabold ${member.is_published ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>{t(member.is_published ? 'memberActive' : 'draft')}</span>
          </button>)}</div>
          <div className="mt-4"><Pagination page={page} count={count} onChange={setPage} /></div>
        </> : <div className="py-12 text-center"><UsersRound className="mx-auto text-slate-300" size={28} /><p className="mt-3 text-sm font-bold text-slate-700">{t('noActiveMembersAdmin')}</p><p className="mt-1 text-xs text-slate-500">{t('createFirstMember')}</p></div>}
      </Card>

      <ResponsiveDetailPanel open={editorOpen} onClose={() => { setSelected(null); setEditorOpen(false); }} label={selected ? t('editMember') : t('newMember')}>
      <Card className="!border-0 !bg-white !p-0 !shadow-none 2xl:!border-slate-200 2xl:!p-5 2xl:!shadow-sm">
        <div className="mb-5 flex items-start justify-between gap-4"><h2 className="font-heading text-lg font-extrabold text-slate-900">{selected ? t('editMember') : t('newMember')}</h2>{editorOpen && <button type="button" onClick={() => { setSelected(null); setEditorOpen(false); }} className="grid h-8 w-8 cursor-pointer place-items-center rounded-lg text-slate-400 hover:bg-slate-100" aria-label={t('close')}><X size={17} /></button>}</div>
        {selected?.image && !form.image && <div className="mb-4 flex items-center gap-3"><MemberAvatar member={selected} size="lg" /><span className="text-xs text-slate-500">{t('memberPhoto')}</span></div>}
        <form className="space-y-4" onSubmit={saveMember}>
          <Input id="active-member-name" name="name" label={t('memberName')} required maxLength={150} value={form.name} onChange={updateField} />
          <Input id="active-member-designation" name="designation" label={t('memberDesignation')} maxLength={150} value={form.designation} onChange={updateField} />
          <Input id="active-member-social" name="social_url" label={t('memberSocialUrl')} type="url" required value={form.social_url} onChange={updateField} />
          <Input id="active-member-image" name="image" label={t('memberPhoto')} type="file" accept="image/jpeg,image/png,image/webp" onChange={updateField} />
          <div className="grid gap-4 sm:grid-cols-2">
            <Input id="active-member-order" name="display_order" label={t('memberOrder')} type="number" min="0" step="1" required value={form.display_order} onChange={updateField} />
            <label className="flex min-h-11 cursor-pointer items-center gap-3 self-end rounded-xl bg-slate-50 p-3 text-sm font-semibold text-slate-700"><input type="checkbox" name="is_published" checked={form.is_published} onChange={updateField} className="h-4 w-4 accent-red-700" />{t('memberIsActive')}</label>
          </div>
          <div className="flex flex-wrap gap-3"><Button type="submit" variant="primary" loading={saving} className="flex-1 !rounded-xl"><Save size={16} /> {t('saveMember')}</Button>{selected && <Button type="button" disabled={deleting} onClick={deleteMember} className="!rounded-xl !text-red-700"><Trash2 size={16} /> {t('deleteMember')}</Button>}</div>
        </form>
      </Card>
      </ResponsiveDetailPanel>
    </div>
  </ContentManagerFrame>;
}

function NoticeManager() {
  const { t, lang } = useLang();
  const [notices, setNotices] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [form, setForm] = useState(emptyNotice);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');
  const [feedback, setFeedback] = useState('');

  const loadNotices = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiGet(`${API_ENDPOINTS.adminNotices}?page=${page}`);
      const results = Array.isArray(data) ? data : data?.results || [];
      setNotices(results);
      setCount(Array.isArray(data) ? results.length : data?.count || 0);
      setSelected((current) => current ? results.find((item) => item.id === current.id) || null : null);
    } catch (err) {
      setError(err.message);
      setNotices([]);
      setCount(0);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => { loadNotices(); }, [loadNotices]);

  useEffect(() => {
    setForm(selected ? { title: selected.title || '', content: selected.content || '', is_published: Boolean(selected.is_published) } : emptyNotice);
  }, [selected]);

  function updateField(event) {
    const { name, value, checked, type } = event.target;
    setForm((current) => ({ ...current, [name]: type === 'checkbox' ? checked : value }));
  }

  async function saveNotice(event) {
    event.preventDefault();
    setSaving(true);
    setError('');
    setFeedback('');
    try {
      const saved = selected
        ? await apiPatch(API_ENDPOINTS.adminNoticeDetail(selected.id), form)
        : await apiPost(API_ENDPOINTS.adminNotices, form);
      setNotices((current) => selected ? current.map((item) => item.id === saved.id ? saved : item) : [saved, ...current].slice(0, 20));
      setCount((current) => selected ? current : current + 1);
      setSelected(saved);
      setFeedback(t('noticeSaved'));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function deleteNotice() {
    if (!selected || !window.confirm(t('confirmDeleteNotice'))) return;
    setDeleting(true);
    setError('');
    setFeedback('');
    try {
      await apiDelete(API_ENDPOINTS.adminNoticeDetail(selected.id));
      setNotices((current) => current.filter((item) => item.id !== selected.id));
      setCount((current) => Math.max(0, current - 1));
      setSelected(null);
      setEditorOpen(false);
      setFeedback(t('noticeDeleted'));
    } catch (err) {
      setError(err.message);
    } finally {
      setDeleting(false);
    }
  }

  function formatPublishedDate(value) {
    if (!value) return '';
    return new Intl.DateTimeFormat(lang === 'bn' ? 'bn-BD' : 'en-US', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
  }

  return <ContentManagerFrame error={error} feedback={feedback}>
    <div className="grid items-start gap-5 2xl:grid-cols-[1.1fr_.9fr]">
      <Card className="!border-slate-200 !bg-white !p-4 !shadow-sm sm:!p-5">
        <div className="mb-4 flex items-center justify-between gap-3"><h2 className="font-heading text-lg font-extrabold text-slate-900">{t('managePublicNotices')}</h2><Button type="button" variant="primary" onClick={() => { setSelected(null); setEditorOpen(true); setError(''); setFeedback(''); }}><Plus size={16} /> {t('newNotice')}</Button></div>
        {loading ? <div className="py-12"><Spinner label={t('loading')} /></div> : notices.length ? <>
          <div className="space-y-2">{notices.map((item) => <button key={item.id} type="button" onClick={() => { setSelected(item); setEditorOpen(true); setFeedback(''); setError(''); }} className={`flex w-full cursor-pointer items-start gap-3 rounded-xl border p-3 text-left transition-colors hover:border-rose-200 hover:bg-rose-50/40 ${selected?.id === item.id ? 'border-rose-200 bg-rose-50/50' : 'border-slate-100 bg-white'}`}>
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-rose-50 text-brand"><FileText size={18} /></span>
            <span className="min-w-0 flex-1"><span className="flex flex-wrap items-center gap-2"><span className="truncate text-sm font-extrabold text-slate-800">{item.title}</span><span className={`rounded-full px-2 py-0.5 text-[10px] font-extrabold ${item.is_published ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>{t(item.is_published ? 'published' : 'draft')}</span></span><span className="mt-1 block line-clamp-2 text-xs leading-5 text-slate-500">{item.content}</span>{item.published_at && <span className="mt-1 block text-[11px] text-slate-400">{formatPublishedDate(item.published_at)}</span>}</span>
          </button>)}</div>
          <div className="mt-4"><Pagination page={page} count={count} onChange={setPage} /></div>
        </> : <div className="py-12 text-center"><FileText className="mx-auto text-slate-300" size={28} /><p className="mt-3 text-sm font-bold text-slate-700">{t('noAdminNotices')}</p><p className="mt-1 text-xs text-slate-500">{t('createFirstNotice')}</p></div>}
      </Card>

      <ResponsiveDetailPanel open={editorOpen} onClose={() => { setSelected(null); setEditorOpen(false); }} label={selected ? t('editNotice') : t('newNotice')}>
      <Card className="!border-0 !bg-white !p-0 !shadow-none 2xl:!border-slate-200 2xl:!p-5 2xl:!shadow-sm">
        <div className="mb-5 flex items-start justify-between gap-4"><h2 className="font-heading text-lg font-extrabold text-slate-900">{selected ? t('editNotice') : t('newNotice')}</h2>{editorOpen && <button type="button" onClick={() => { setSelected(null); setEditorOpen(false); }} className="grid h-8 w-8 cursor-pointer place-items-center rounded-lg text-slate-400 hover:bg-slate-100" aria-label={t('close')}><X size={17} /></button>}</div>
        <form className="space-y-4" onSubmit={saveNotice}>
          <Input id="notice-title" name="title" label={t('noticeTitleField')} required maxLength={255} value={form.title} onChange={updateField} />
          <Textarea id="notice-content" name="content" label={t('noticeBodyField')} required rows={7} value={form.content} onChange={updateField} />
          <label className="flex cursor-pointer items-center gap-3 rounded-xl bg-slate-50 p-3 text-sm font-semibold text-slate-700"><input type="checkbox" name="is_published" checked={form.is_published} onChange={updateField} className="h-4 w-4 accent-red-700" />{t('noticePublished')}</label>
          <div className="flex flex-wrap gap-3"><Button type="submit" variant="primary" loading={saving} className="flex-1 !rounded-xl"><Save size={16} /> {t('saveNotice')}</Button>{selected && <Button type="button" disabled={deleting} onClick={deleteNotice} className="!rounded-xl !text-red-700"><Trash2 size={16} /> {t('deleteNotice')}</Button>}</div>
        </form>
      </Card>
      </ResponsiveDetailPanel>
    </div>
  </ContentManagerFrame>;
}

function ContentManagerFrame({ error, feedback, children }) {
  return <div className="space-y-4">{error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</p>}{feedback && <p role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{feedback}</p>}{children}</div>;
}
