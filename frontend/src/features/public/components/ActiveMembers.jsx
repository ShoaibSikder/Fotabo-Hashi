import { useState } from 'react';
import { ExternalLink } from 'lucide-react';
import { useLang } from '../../../contexts/LanguageContext.jsx';
import Avatar from '../../../components/ui/Avatar.jsx';
import EmptyState from '../../../components/ui/EmptyState.jsx';

function MemberAvatar({ member }) {
  const [failed, setFailed] = useState(false);

  if (!member.image || failed) {
    return <Avatar name={member.name} size="lg" className="mx-auto h-20 w-20 text-xl" />;
  }

  return (
    <img
      src={member.image}
      alt={`${member.name} profile`}
      loading="lazy"
      onError={() => setFailed(true)}
      className="mx-auto h-20 w-20 rounded-full border-2 border-white object-cover shadow-sm"
    />
  );
}

function MemberCard({ member }) {
  const { t } = useLang();
  const content = <>
    <MemberAvatar member={member} />
    <h3 className="mt-3 line-clamp-2 font-extrabold text-brand-dark">{member.name}</h3>
    {member.designation && <p className="mt-1 line-clamp-1 text-xs font-semibold text-muted">{member.designation}</p>}
    <span className="sr-only">{t('openMemberSocial')}</span>
    <ExternalLink aria-hidden="true" size={15} className="absolute right-4 top-4 text-slate-400 transition-colors group-hover:text-brand" />
  </>;
  const classes = 'neu group relative flex min-h-36 snap-start flex-col items-center justify-center p-4 text-center transition-colors hover:bg-rose-50/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand';

  if (!member.social_url) {
    return <article className={classes} aria-label={member.name}>{content}</article>;
  }

  return <a className={classes} href={member.social_url} target="_blank" rel="noopener noreferrer" aria-label={t('memberSocialLink', { name: member.name })}>{content}</a>;
}

export default function ActiveMembers({ members = [] }) {
  const { t } = useLang();
  return (
    <section id="active-members" className="page-shell scroll-mt-24 py-12 sm:py-16">
      <div className="mx-auto max-w-2xl text-center">
        <p className="eyebrow mb-3">{t('activeMembersIntro')}</p>
        <h2 className="section-title">{t('activeMembers')}</h2>
      </div>
      {members.length ? (
        <div
          className="mt-8 grid auto-cols-[minmax(220px,75vw)] grid-flow-col grid-rows-2 gap-4 overflow-x-auto overscroll-x-contain pb-3 snap-x snap-mandatory focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-brand md:auto-cols-[minmax(220px,30vw)] lg:auto-cols-[260px] lg:grid-rows-1"
          tabIndex={0}
          aria-label={t('activeMembersSlider')}
        >
          {members.map((member) => <MemberCard key={member.id} member={member} />)}
        </div>
      ) : (
        <div className="mt-7"><EmptyState title={t('activeMembersEmptyTitle')} description={t('activeMembersEmptyBody')} /></div>
      )}
    </section>
  );
}
