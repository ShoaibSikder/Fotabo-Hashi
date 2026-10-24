import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  Facebook,
  Globe2,
  Github,
  Heart,
  Linkedin,
  Mail,
  MapPin,
  Phone,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useLang } from "../../contexts/LanguageContext.jsx";
import { apiGet } from "../../services/apiClient.js";
import { API_ENDPOINTS } from "../../services/endpointConfig.js";

const companyLinks = [
  { label: "aboutEyebrow", to: "/#about" },
  { label: "contactUs", to: "https://www.facebook.com/fotabo.hasi" },
  { label: "becomeDonor", to: "/register" },
  { label: "notices", to: "/#notices" },
];

const quickLinks = [
  { label: "findDonor", to: "/donors" },
  { label: "requestBlood", to: "/requests/new" },
  { label: "leaderboard", to: "/leaderboard" },
];

const developerSocialLinks = [
  {
    label: "Portfolio",
    href:
      import.meta.env.VITE_DEVELOPER_PORTFOLIO_URL ||
      "https://shoaibsikderportfolio.vercel.app",
    Icon: Globe2,
  },
  {
    label: "Facebook",
    href:
      import.meta.env.VITE_DEVELOPER_FACEBOOK_URL ||
      "https://www.facebook.com/shoaib.sikder.35",
    Icon: Facebook,
  },
  {
    label: "LinkedIn",
    href:
      import.meta.env.VITE_DEVELOPER_LINKEDIN_URL ||
      "https://www.linkedin.com/in/md-shoaib-sikder-232abb3b3/",
    Icon: Linkedin,
  },
  {
    label: "GitHub",
    href:
      import.meta.env.VITE_DEVELOPER_GITHUB_URL ||
      "https://github.com/ShoaibSikder",
    Icon: Github,
  },
];

function FooterLink({ label, to, t, onContactClick }) {
  const className =
    "group inline-flex cursor-pointer items-center gap-2 text-sm text-rose-100/75 transition-colors hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-rose-200";
  const content = (
    <>
      {t(label)}
      <ArrowUpRight
        size={14}
        className="transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
      />
    </>
  );

  if (to.startsWith("/")) {
    return (
      <Link className={className} to={to}>
        {content}
      </Link>
    );
  }

  return (
    <a
      className={className}
      href={to}
      target={to.startsWith("http") ? "_blank" : undefined}
      rel={to.startsWith("http") ? "noreferrer" : undefined}
      onClick={onContactClick}
    >
      {content}
    </a>
  );
}

export default function PublicFooter() {
  const { t } = useLang();
  const [organization, setOrganization] = useState(null);

  useEffect(() => {
    apiGet(API_ENDPOINTS.organization)
      .then(setOrganization)
      .catch(() => {});
  }, []);

  return (
    <footer className="bg-[#361414] text-white">
      <div className="page-shell grid gap-10 py-12 sm:py-14 lg:grid-cols-[1.35fr_.8fr_.9fr_1.25fr] lg:gap-8 lg:py-16">
        <div>
          <Link
            to="/"
            className="inline-flex items-center gap-2.5 font-heading text-xl font-extrabold tracking-tight text-white"
          >
            <img
              src="/images/fotabo-hashi-logo.webp"
              alt=""
              className="h-10 w-10 object-contain"
            />
            {organization?.name || "Fotabo Hashi"}
          </Link>
          <p className="mt-4 max-w-sm text-sm leading-6 text-rose-100/75">
            {t("footerTagline")}
          </p>
          <p className="mt-4 inline-flex items-start gap-2 text-sm leading-6 text-rose-100/65">
            <MapPin size={16} className="mt-1 shrink-0 text-red-300" />
            {organization?.address || t("footerLocation")}
          </p>
          <div
            className="mt-4 flex flex-col items-start gap-2.5"
            aria-label="Fotabo Hashi contact links"
          >
            <a
              href="mailto:fotabohasi@gmail.com"
              className="inline-flex items-start gap-2 text-sm leading-6 text-rose-100/65 transition-colors hover:text-white"
              aria-label="Email Fotabo Hashi"
            >
              <Mail size={16} className="mt-1 shrink-0 text-red-300" />
              fotabohasi@gmail.com
            </a>
            <div className="flex items-center gap-2.5">
              <a
                href="https://www.facebook.com/fotabo.hasi"
                target="_blank"
                rel="noreferrer"
                aria-label="Fotabo Hashi on Facebook"
                title="Fotabo Hashi on Facebook"
                className="grid h-9 w-9 place-items-center rounded-full bg-white/10 text-rose-100/85 transition-colors hover:bg-white/20 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-rose-200"
              >
                <Facebook size={17} />
              </a>
              <a
                href="mailto:fotabohasi@gmail.com"
                aria-label="Email Fotabo Hashi"
                title="fotabohasi@gmail.com"
                className="grid h-9 w-9 place-items-center rounded-full bg-white/10 text-rose-100/85 transition-colors hover:bg-white/20 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-rose-200"
              >
                <Mail size={17} />
              </a>
            </div>
          </div>
        </div>

        <nav aria-label={t("company")}>
          <h2 className="text-sm font-extrabold text-white">{t("company")}</h2>
          <ul className="mt-5 space-y-3">
            {companyLinks.map(({ label, to }) => (
              <li key={label}>
                <FooterLink label={label} to={to} t={t} />
              </li>
            ))}
          </ul>
        </nav>

        <nav aria-label={t("quickLinks")}>
          <h2 className="text-sm font-extrabold text-white">
            {t("quickLinks")}
          </h2>
          <ul className="mt-5 space-y-3">
            {quickLinks.map(({ label, to }) => (
              <li key={label}>
                <FooterLink label={label} to={to} t={t} />
              </li>
            ))}
          </ul>
        </nav>

        <section
          id="footer-contact"
          aria-labelledby="footer-developer-heading"
          className="scroll-mt-24"
        >
          <h2
            id="footer-developer-heading"
            className="text-sm font-extrabold text-white"
          >
            {t("developer")}
          </h2>
          <div className="mt-4 flex items-center gap-4">
            <img
              src="/images/developer.jpg"
              alt="MD. Shoaib Sikder"
              className="h-16 w-16 shrink-0 rounded-full border-2 border-white/15 object-cover"
              loading="lazy"
            />
            <div>
              <p className="text-sm font-semibold text-rose-50">
                MD. Shoaib Sikder
              </p>
              <div className="mt-3 flex items-center gap-2">
                {developerSocialLinks.map(({ label, href, Icon }) => (
                  <a
                    key={label}
                    href={href}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={`MD. Shoaib Sikder on ${label}`}
                    title={label}
                    className="grid h-8 w-8 cursor-pointer place-items-center rounded-full bg-white/10 text-rose-100/85 transition-colors hover:bg-white/20 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-rose-200"
                  >
                    <Icon size={17} />
                  </a>
                ))}
              </div>
            </div>
          </div>
          {(organization?.email || organization?.phone) && (
            <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-xs text-rose-100/70">
              {organization.email && (
                <a
                  className="inline-flex items-center gap-1.5 hover:text-white"
                  href={`mailto:${organization.email}`}
                >
                  <Mail size={14} />
                  {organization.email}
                </a>
              )}
              {organization.phone && (
                <a
                  className="inline-flex items-center gap-1.5 hover:text-white"
                  href={`tel:${organization.phone}`}
                >
                  <Phone size={14} />
                  {organization.phone}
                </a>
              )}
            </div>
          )}
        </section>
      </div>

      <div className="border-t border-white/10">
        <div className="page-shell flex flex-col gap-4 py-5 text-xs text-rose-100/60 sm:flex-row sm:items-center sm:justify-between">
          <p>
            © {new Date().getFullYear()} {organization?.name || "Fotabo Hashi"}{" "}
            <span className="mx-1.5">·</span> {t("allRightsReserved")}
          </p>
        </div>
      </div>
    </footer>
  );
}
