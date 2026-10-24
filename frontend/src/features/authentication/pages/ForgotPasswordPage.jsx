import { useState } from 'react';
import { Link } from 'react-router-dom';
import { MailQuestion } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Input from '../../../components/ui/Input.jsx';
import Button from '../../../components/ui/Button.jsx';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { apiPost } from '../../../services/apiClient.js';

export default function ForgotPasswordPage() {
  const [email,setEmail]=useState(''); const [busy,setBusy]=useState(false); const [message,setMessage]=useState(''); const [error,setError]=useState('');
  async function submit(event){event.preventDefault();setBusy(true);setMessage('');setError('');try{const result=await apiPost(API_ENDPOINTS.passwordReset,{email});setMessage(result.message||'If an account exists for that email, reset instructions have been sent.');}catch(err){setError(err.message);}finally{setBusy(false);}}
  return <div className="page-shell grid min-h-[65vh] place-items-center py-12"><Card className="w-full max-w-lg"><span className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-soft text-brand"><MailQuestion/></span><h1 className="mt-5 text-2xl font-extrabold text-brand-dark">Reset your password</h1><p className="mt-3 leading-7 text-muted">Enter your account email. If it matches an account, we’ll send a secure reset link.</p><form onSubmit={submit} className="mt-6 space-y-4">{message&&<p role="status" className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">{message}</p>}{error&&<p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{error}</p>}<Input id="reset-email" label="Email address" type="email" autoComplete="email" required value={email} onChange={e=>setEmail(e.target.value)}/><Button type="submit" variant="primary" loading={busy} className="w-full">Send reset link</Button></form><Link className="mt-5 inline-flex text-sm font-bold text-brand hover:underline" to="/login">Back to sign in</Link></Card></div>;
}
