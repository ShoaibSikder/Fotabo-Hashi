import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { KeyRound } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Input from '../../../components/ui/Input.jsx';
import Button from '../../../components/ui/Button.jsx';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { apiPost } from '../../../services/apiClient.js';

export default function ResetPasswordPage() {
  const [params]=useSearchParams(); const uid=params.get('uid')||''; const token=params.get('token')||'';
  const [password,setPassword]=useState(''); const [confirmation,setConfirmation]=useState(''); const [busy,setBusy]=useState(false); const [done,setDone]=useState(false); const [error,setError]=useState('');
  async function submit(event){event.preventDefault();setError('');if(password!==confirmation){setError('The passwords do not match.');return;}setBusy(true);try{await apiPost(API_ENDPOINTS.passwordResetConfirm,{uid,token,new_password:password});setDone(true);}catch(err){setError(err.message);}finally{setBusy(false);}}
  return <div className="page-shell grid min-h-[65vh] place-items-center py-12"><Card className="w-full max-w-lg"><span className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-soft text-brand"><KeyRound/></span><h1 className="mt-5 text-2xl font-extrabold text-brand-dark">Choose a new password</h1>{done?<><p role="status" className="mt-3 leading-7 text-emerald-800">Your password was changed. Sign in with the new password.</p><Link className="mt-5 inline-flex font-bold text-brand hover:underline" to="/login">Go to sign in</Link></>:!uid||!token?<><p className="mt-3 leading-7 text-muted">This reset link is incomplete. Request a new link to continue.</p><Link className="mt-5 inline-flex font-bold text-brand hover:underline" to="/forgot-password">Request reset link</Link></>:<><p className="mt-3 leading-7 text-muted">Choose a new password for your account.</p><form onSubmit={submit} className="mt-6 space-y-4">{error&&<p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{error}</p>}<Input id="new-password" label="New password" type="password" autoComplete="new-password" required minLength="8" hint="At least 8 characters." value={password} onChange={e=>setPassword(e.target.value)}/><Input id="confirm-password" label="Confirm new password" type="password" autoComplete="new-password" required value={confirmation} onChange={e=>setConfirmation(e.target.value)}/><Button type="submit" variant="primary" loading={busy} className="w-full">Change password</Button></form></>}</Card></div>;
}
