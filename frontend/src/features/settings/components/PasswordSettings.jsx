import { useState } from 'react';
import { KeyRound } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Card from '../../../components/ui/Card.jsx';
import Input from '../../../components/ui/Input.jsx';
import Button from '../../../components/ui/Button.jsx';
import { useAuthCtx } from '../../../contexts/AuthContext.jsx';
import { apiPost } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function PasswordSettings() {
  const { t } = useLang();
  const { clearSession }=useAuthCtx(); const navigate=useNavigate();
  const [form,setForm]=useState({current_password:'',new_password:'',confirm_password:''});
  const [busy,setBusy]=useState(false); const [error,setError]=useState(''); const [message,setMessage]=useState('');
  function change(event){setForm(current=>({...current,[event.target.name]:event.target.value}));}
  async function submit(event){event.preventDefault();setError('');setMessage('');if(form.new_password!==form.confirm_password){setError(t('passwordMismatch'));return;}setBusy(true);try{const result=await apiPost(API_ENDPOINTS.passwordChange,{current_password:form.current_password,new_password:form.new_password});setMessage(result.message||t('passwordChangedReauth'));clearSession();setTimeout(()=>navigate('/login',{replace:true}),900);}catch(err){setError(err.message);}finally{setBusy(false);}}
  return <Card><div className="flex gap-4"><span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-brand-soft text-brand"><KeyRound/></span><div className="min-w-0 flex-1"><h2 className="font-extrabold text-brand-dark">{t('passwordSecurity')}</h2><p className="mt-1 text-sm text-muted">{t('passwordSecurityHelp')}</p><form onSubmit={submit} className="mt-5 space-y-4">{error&&<p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{error}</p>}{message&&<p role="status" className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">{message}</p>}<Input id="current_password" name="current_password" type="password" autoComplete="current-password" label={t('currentPassword')} required value={form.current_password} onChange={change}/><Input id="new_password" name="new_password" type="password" autoComplete="new-password" label={t('newPassword')} required minLength="8" hint={t('passwordMinimum')} value={form.new_password} onChange={change}/><Input id="confirm_password" name="confirm_password" type="password" autoComplete="new-password" label={t('confirmNewPassword')} required value={form.confirm_password} onChange={change}/><div className="flex justify-end"><Button type="submit" variant="primary" loading={busy}>{t('changePassword')}</Button></div></form></div></div></Card>;
}
